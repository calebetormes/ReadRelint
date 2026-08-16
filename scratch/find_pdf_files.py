import os

search_paths = ["d:\\www", "C:\\Users\\admin\\Desktop", "C:\\Users\\admin\\Downloads"]

found_pdfs = []
for sp in search_paths:
    if os.path.exists(sp):
        for root, dirs, files in os.walk(sp):
            for f in files:
                if f.lower().endswith('.pdf'):
                    found_pdfs.append(os.path.join(root, f))

print(f"Encontrados {len(found_pdfs)} arquivos PDF:")
for pdf in found_pdfs[:20]:
    print(f" - {pdf}")
