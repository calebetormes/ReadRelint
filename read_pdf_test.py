import sys
from pathlib import Path
from src.adapters.pdf_reader import PdfReader

def main():
    if len(sys.argv) < 2:
        print("Uso: .venv\\Scripts\\python.exe read_pdf_test.py <caminho_do_arquivo.pdf>")
        # Se nenhum argumento for passado, podemos pedir interativamente
        pdf_path_str = input("Por favor, insira o caminho completo para o arquivo PDF: ").strip()
    else:
        pdf_path_str = sys.argv[1]

    pdf_path = Path(pdf_path_str.strip('"'))

    if not pdf_path.exists():
        print(f"Erro: O arquivo '{pdf_path}' não foi encontrado.")
        sys.exit(1)

    print(f"\nLendo o arquivo: {pdf_path.name}...")
    print("-" * 50)
    
    reader = PdfReader()
    try:
        extracted_text = reader.extract_text(pdf_path)
        print("\n=== TEXTO EXTRAÍDO COM SUCESSO ===")
        print(extracted_text)
        print("===================================\n")
        print(f"Total de caracteres lidos: {len(extracted_text)}")
    except Exception as e:
        print(f"Erro durante a extração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
