"""Adapter para extração de texto e imagens de PDFs usando Docling + PyMuPDF."""
import re
import hashlib
from pathlib import Path
from src.engine.parsers.file_parser import IFileParser
from src.engine.cleaners.text_cleaner import is_invalid_caption

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    DocumentConverter = None

import pymupdf


def _postprocess_docling_markdown(md: str) -> str:
    """
    Pós-processa o Markdown exportado pelo Docling para remover artefatos
    que prejudicam a qualidade do texto sem LLM.
    """
    if not md:
        return ""

    # Remove marcadores de imagem <!-- image -->
    md = re.sub(r'<!--\s*image\s*-->', '', md, flags=re.IGNORECASE)

    # Remove linhas de separador visual isoladas (___, ---, ===, ***)
    md = re.sub(r'(?m)^[ \t]*(?:[_\-=\*]{3,})[ \t]*$', '', md)

    # Colapsa 3+ linhas em branco consecutivas para no máximo 1 linha vazia
    md = re.sub(r'\n{3,}', '\n\n', md)

    # Remove espaços/tabs antes das quebras de linha
    md = re.sub(r'[ \t]+\n', '\n', md)

    return md.strip()


class DoclingPdfReader(IFileParser):
    """
    Implementação avançada (Adapter) para extração de texto de arquivos PDF
    utilizando a biblioteca Docling para parsing estruturado de tabelas e layouts,
    combinada com PyMuPDF para a extração inteligente de imagens.
    """
    def __init__(self):
        if DocumentConverter is None:
            raise ImportError("Docling não está instalado. Rode 'pip install docling'.")
        self.converter = DocumentConverter()

    def extract_text(self, file_path: Path) -> str:
        """
        Extrai texto do PDF usando o Docling para exportar Markdown estruturado,
        aplicando pós-processamento para remover artefatos do Markdown.
        """
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        try:
            # Converte o documento para a representação interna do Docling
            result = self.converter.convert(str(path_obj))
            # Exporta para Markdown estruturado
            raw_markdown = result.document.export_to_markdown()
            # Pós-processamento para remover artefatos
            return _postprocess_docling_markdown(raw_markdown)
        except Exception as e:
            raise ValueError(
                f"Falha ao processar o PDF com Docling: {file_path}. Detalhes: {e}"
            ) from e

    def extract_images(self, file_path: Path, output_dir: Path) -> list:
        """
        Extrai imagens utilizando o mecanismo geométrico do PyMuPDF.
        Ignora brasões da BM e extrai legendas válidas (descartando texto de rodapé).
        """
        path_obj = Path(file_path)
        if not path_obj.exists():
            return []

        out_path = Path(output_dir)
        extracted_images = []
        seen_hashes = set()

        try:
            doc = pymupdf.open(path_obj)
            img_counter = 1
            for page_index in range(len(doc)):
                page = doc[page_index]
                try:
                    page_height = float(page.rect.height)
                except Exception:
                    page_height = 842.0

                image_list = page.get_images(full=True)

                for img_info in image_list:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    if not base_image:
                        continue

                    image_bytes = base_image.get("image")
                    image_ext = base_image.get("ext", "png")
                    width = base_image.get("width", 0)
                    height = base_image.get("height", 0)

                    # Se a imagem for vazia, não há o que processar
                    if not image_bytes:
                        continue

                    # 1. Filtro de tamanho mínimo: ignora ícones/pequenos detalhes (< 50px ou < 1KB)
                    if width < 50 or height < 50 or len(image_bytes) < 1024:
                        continue

                    # 2. Filtro de duplicidade (Marcas d'água / Logos que se repetem em múltiplas páginas)
                    img_hash = hashlib.sha256(image_bytes).hexdigest()
                    if img_hash in seen_hashes:
                        continue
                    seen_hashes.add(img_hash)

                    # 3. Filtro de Posição de Cabeçalho: Descarta Logo/Brasão da BM no topo da PRIMEIRA PÁGINA
                    if page_index == 0:
                        try:
                            rects = page.get_image_rects(xref)
                            if isinstance(rects, (list, tuple)) and rects:
                                y0 = float(rects[0].y0)
                                if y0 < 140 or (y0 / page_height) < 0.18:
                                    continue
                        except Exception:
                            pass

                    # 4. Extração de Legenda do Texto do PDF (Texto logo abaixo ou acima da imagem)
                    caption = ""
                    try:
                        rects = page.get_image_rects(xref)
                        if isinstance(rects, (list, tuple)) and rects:
                            r = rects[0]
                            page_w = float(page.rect.width) if hasattr(page, "rect") else 595.0
                            page_h = float(page.rect.height) if hasattr(page, "rect") else 842.0

                            # Busca texto em caixa abaixo da imagem (até 45pt abaixo)
                            clip_below = pymupdf.Rect(max(0.0, float(r.x0) - 30.0), float(r.y1), min(page_w, float(r.x1) + 30.0), min(page_h, float(r.y1) + 45.0))
                            cap_text = str(page.get_text("text", clip=clip_below)).strip()

                            # Se não encontrou abaixo, busca texto em caixa acima da imagem (até 35pt acima)
                            if not cap_text:
                                clip_above = pymupdf.Rect(max(0.0, float(r.x0) - 30.0), max(0.0, float(r.y0) - 35.0), min(page_w, float(r.x1) + 30.0), float(r.y0))
                                cap_text = str(page.get_text("text", clip=clip_above)).strip()

                            if cap_text and not is_invalid_caption(cap_text):
                                clean_cap = " ".join(cap_text.split())
                                if len(clean_cap) > 200:
                                    clean_cap = clean_cap[:197] + "..."
                                caption = clean_cap
                    except Exception:
                        pass

                    # Garante que a pasta no disco só seja criada ao encontrar uma imagem válida
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
            doc.close()
        except Exception:
            pass

        return extracted_images
