import sys
from pathlib import Path
sys.path.insert(0, '.')

from src.adapters.pdf_reader import PdfReader

reader = PdfReader()
testez_dir = Path(r"C:\Users\admin\Desktop\testez")

for pdf_file in testez_dir.glob("*.pdf"):
    print(f"\n==================== {pdf_file.name} ====================")
    text = reader.extract_text(pdf_file)
    # Print lines that contain NOME, ALCUNHA, RG, CPF, VITIMA, SUSPEITO, ACUSADO, ENVOLVIDO
    lines = text.split('\n')
    for line in lines:
        l_upper = line.upper()
        if any(k in l_upper for k in ["NOME", "ALCUNHA", "VULGO", "RG", "CPF", "VÍTIMA", "VITIMA", "SUSPEITO", "ACUSADO", "ENVOLVIDO", "TESTEMUNHA"]):
            print(f"  {line.strip()}")
