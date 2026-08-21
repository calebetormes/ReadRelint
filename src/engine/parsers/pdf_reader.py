import hashlib
import pymupdf
from pathlib import Path
from typing import Optional
from src.engine.parsers.file_parser import IFileParser
from src.engine.cleaners.text_cleaner import is_invalid_caption


class PdfReader(IFileParser):
    """
    Implementação concreta (Adapter) para extração de texto e imagens de arquivos PDF
    utilizando a biblioteca PyMuPDF (fitz).
    """

    def extract_text(self, file_path: Path) -> str:
        """
        Abre o PDF informado, extrai o texto de todas as páginas e o concatena.

        :param file_path: Caminho completo para o arquivo PDF.
        :return: Texto bruto extraído e concatenado das páginas do PDF.
        :raises FileNotFoundError: Se o arquivo especificado não existir.
        :raises ValueError: Se o arquivo não puder ser lido ou estiver corrompido.
        """
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        try:
            doc = pymupdf.open(path_obj)
        except Exception as e:
            raise ValueError(f"Falha ao abrir o arquivo PDF: {file_path}. Detalhes: {e}")

        text_pages = []
        try:
            for page in doc:
                text_pages.append(page.get_text())
        except Exception as e:
            raise ValueError(f"Erro ao ler conteúdo das páginas do PDF: {file_path}. Detalhes: {e}")
        finally:
            doc.close()

        return "\n".join(text_pages)

    def extract_images(self, file_path: Path, output_dir: Path) -> list:
        """
        Extrai imagens do arquivo PDF informado, ignorando automaticamente o logo/brasão
        da Brigada Militar (posicionado no cabeçalho), marcas d'água repetitivas e ícones.

        :param file_path: Caminho completo para o arquivo PDF.
        :param output_dir: Pasta de destino onde as imagens serão salvas.
        :return: Lista de dicionários contendo metadados das imagens extraídas.
        """
        path_obj = Path(file_path)
        if not path_obj.exists():
            return []

        out_path = Path(output_dir)
        extracted_images = []
        seen_hashes: set = set()

        doc = None
        try:
            doc = pymupdf.open(path_obj)
            img_counter = 1
            for page_index, page in enumerate(doc):
                try:
                    page_height = float(page.rect.height)
                except Exception:
                    page_height = 842.0

                for img_info in page.get_images(full=True):
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    if not base_image:
                        continue

                    image_bytes = base_image.get("image")
                    image_ext = base_image.get("ext", "png")
                    width = base_image.get("width", 0)
                    height = base_image.get("height", 0)

                    # Guard de tipo: image_bytes deve ser bytes para continuar
                    if not image_bytes:
                        continue

                    if not self._is_valid_image(image_bytes, width, height, seen_hashes, page_index, page, xref, page_height):
                        continue

                    caption = self._extract_caption(page, xref)

                    if not out_path.exists():
                        out_path.mkdir(parents=True, exist_ok=True)

                    img_filename = f"img_{img_counter:02d}.{image_ext}"
                    save_path = out_path / img_filename
                    save_path.write_bytes(image_bytes)

                    aspect_ratio = width / height if height > 0 else 1.0
                    extracted_images.append({
                        "file_path": str(save_path).replace("\\", "/"),
                        "width": width,
                        "height": height,
                        "aspect_ratio": aspect_ratio,
                        "caption": caption,
                        "page": page_index + 1
                    })
                    img_counter += 1

        except Exception:
            pass
        finally:
            if doc:
                doc.close()

        return extracted_images

    def _is_valid_image(
        self,
        image_bytes: bytes,
        width: int,
        height: int,
        seen_hashes: set,
        page_index: int,
        page,
        xref: int,
        page_height: float
    ) -> bool:
        """
        Aplica os filtros de validação de imagem: tamanho mínimo, duplicidade
        e posição de cabeçalho institucional na primeira página.
        """
        # 1. Filtro de tamanho mínimo: ignora ícones/pequenos detalhes (< 50px ou < 1KB)
        if width < 50 or height < 50 or len(image_bytes) < 1024:
            return False

        # 2. Filtro de duplicidade (marcas d'água / logos repetidos em múltiplas páginas)
        img_hash = hashlib.sha256(image_bytes).hexdigest()
        if img_hash in seen_hashes:
            return False
        seen_hashes.add(img_hash)

        # 3. Filtro de posição: descarta logo/brasão da BM no topo da primeira página
        if page_index == 0:
            try:
                rects = page.get_image_rects(xref)
                if isinstance(rects, (list, tuple)) and rects:
                    y0 = float(rects[0].y0)
                    if y0 < 140 or (y0 / page_height) < 0.18:
                        return False
            except Exception:
                pass

        return True

    def _extract_caption(self, page, xref: int) -> str:
        """
        Extrai e valida a legenda da imagem buscando texto imediatamente
        abaixo (até 45pt) e, se vazio, imediatamente acima (até 35pt) da imagem.
        Descarta textos de rodapé institucionais via is_invalid_caption.
        """
        try:
            rects = page.get_image_rects(xref)
            if not (isinstance(rects, (list, tuple)) and rects):
                return ""

            r = rects[0]
            page_w = float(page.rect.width) if hasattr(page, "rect") else 595.0
            page_h = float(page.rect.height) if hasattr(page, "rect") else 842.0

            # Busca texto em caixa abaixo da imagem (até 45pt abaixo)
            clip_below = pymupdf.Rect(
                max(0.0, float(r.x0) - 30.0),
                float(r.y1),
                min(page_w, float(r.x1) + 30.0),
                min(page_h, float(r.y1) + 45.0)
            )
            cap_text = str(page.get_text("text", clip=clip_below)).strip()

            # Se não encontrou abaixo, busca texto em caixa acima da imagem (até 35pt acima)
            if not cap_text:
                clip_above = pymupdf.Rect(
                    max(0.0, float(r.x0) - 30.0),
                    max(0.0, float(r.y0) - 35.0),
                    min(page_w, float(r.x1) + 30.0),
                    float(r.y0)
                )
                cap_text = str(page.get_text("text", clip=clip_above)).strip()

            if not cap_text or is_invalid_caption(cap_text):
                return ""

            clean_cap = " ".join(cap_text.split())
            if len(clean_cap) > 200:
                clean_cap = clean_cap[:197] + "..."

            return clean_cap

        except Exception:
            return ""
