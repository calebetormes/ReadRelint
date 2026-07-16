import sys
from pathlib import Path
from src.adapters.pdf_reader import PdfReader
from src.adapters.ollama_client import OllamaClient
from src.adapters.tinydb_repo import TinyDbRepo
from src.domain.entities import IncidentReport
from src.application.text_cleaner import clean_relint_text

def main():
    if len(sys.argv) < 2:
        print("Uso: .venv\\Scripts\\python.exe run_pipeline_test.py <caminho_do_arquivo.pdf>")
        pdf_path_str = input("Por favor, insira o caminho completo para o arquivo PDF: ").strip()
    else:
        pdf_path_str = sys.argv[1]

    pdf_path = Path(pdf_path_str.strip('"'))

    if not pdf_path.exists():
        print(f"Erro: O arquivo '{pdf_path}' não foi encontrado.")
        sys.exit(1)

    # 1. Extração do Texto do PDF
    print(f"\n[1/3] Extraindo texto do PDF: {pdf_path.name}...")
    reader = PdfReader()
    try:
        raw_text = reader.extract_text(pdf_path)
        extracted_text = clean_relint_text(raw_text)
        print(f"-> Texto extraído e limpo com sucesso! ({len(extracted_text)} caracteres)")
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        sys.exit(1)

    # 2. Processamento com Ollama (IA Local)
    print("\n[2/3] Enviando texto para o Ollama local (esta etapa pode demorar alguns segundos)...")
    llm = OllamaClient(model_name="llama3.1") 
    try:
        content = llm.process_text(extracted_text)
        report = IncidentReport(
            source_file=pdf_path.name,
            content=content
        )
        print("\n=== DADOS ESTRUTURADOS PELA IA ===")
        print(report.model_dump_json(indent=2))
        print("==================================")
    except Exception as e:
        print(f"Erro no processamento da IA: {e}")
        sys.exit(1)

    # 3. Salvamento no banco de dados TinyDB
    db_path = Path("data/database.json")
    print(f"\n[3/3] Salvando no banco de dados local ({db_path})...")
    repo = TinyDbRepo(db_path)
    try:
        doc_id = repo.save(report)
        print(f"-> Sucesso! Relatório salvo com o ID único: {doc_id}")
    except Exception as e:
        print(f"Erro ao salvar no banco: {e}")
        sys.exit(1)

    print("\nProcesso concluído com sucesso!")

if __name__ == "__main__":
    main()
