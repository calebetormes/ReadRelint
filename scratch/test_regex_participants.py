import sys
import os
sys.path.insert(0, '.')
import re
from pathlib import Path
from src.adapters.pdf_reader import PdfReader

reader = PdfReader()
testez_dir = Path(r"C:\Users\admin\Desktop\testez")

def extract_fallback_participants(text: str):
    participants = []
    seen_names = set()

    # 1. Busca por blocos estruturados (ex: NOME: ..., RG: ..., ALCUNHA: ...)
    block_pattern = re.compile(
        r'(?i)NOME:\s*([A-Z\u00C0-\u00FF\s\.]{3,60})\s*\n\s*(?:RG:\s*([\d\.\-]+))?\s*(?:CPF:\s*([\d\.\-]+))?\s*(?:ALCUNHA:\s*([^\n]+))?',
        re.MULTILINE
    )
    for m in block_pattern.finditer(text):
        name = m.group(1).strip()
        rg = (m.group(2) or "").strip()
        cpf = (m.group(3) or "").strip()
        nick = (m.group(4) or "").strip()
        if nick in ["-", "-.", "Não possui", "Nao possui", "N/I", "None"]:
            nick = ""
        doc = cpf if cpf else rg
        
        # Filtra palavras do cabeçalho ou PMs
        upper_name = name.upper()
        if any(bad in upper_name for bad in ["RELATÓRIO", "BRIGADA", "POLÍCIA", "SD ", "SGT ", "CB ", "CAP "]):
            continue
            
        if name and upper_name not in seen_names:
            seen_names.add(upper_name)
            participants.append({
                "name": name.title(),
                "nickname": nick,
                "document": doc,
                "participation_type": "Suspeito"
            })

    # 2. Busca inline por "NOME COMPLETO, RG: 123456" ou "NOME - RG 123456"
    inline_pattern = re.compile(
        r'(?i)\b([A-Z\u00C0-\u00FF]{2,}(?:\s+[A-Z\u00C0-\u00FF]{2,})+)\s*(?:[,\-\–\s]+)(?:RG|CPF)(?:\s*n[º°]|\s*:\s*|\s+)\s*([\d\.\-]+)',
        re.MULTILINE
    )
    for m in inline_pattern.finditer(text):
        name = m.group(1).strip()
        doc = m.group(2).strip()
        upper_name = name.upper()
        
        if any(bad in upper_name for bad in ["RELATÓRIO", "BRIGADA", "POLÍCIA", "SANTOS SILVA", "SD ", "SGT ", "CB ", "CAP "]) and "SANTOS SILVA" not in upper_name:
            if "BRIGADA" in upper_name or "POLÍCIA" in upper_name:
                continue

        if name and upper_name not in seen_names:
            seen_names.add(upper_name)
            participants.append({
                "name": name.title(),
                "nickname": "",
                "document": doc,
                "participation_type": "Acusado"
            })

    return participants


for pdf_file in testez_dir.glob("*.pdf"):
    print(f"\n==================== {pdf_file.name} ====================")
    raw_text = reader.extract_text(pdf_file)
    extracted = extract_fallback_participants(raw_text)
    print(f"Extraídos {len(extracted)} participantes:")
    for p in extracted:
        print(f"  - Nome: {p['name']} | Doc: {p['document']} | Vulgo: {p['nickname']}")
