import sqlite3
import json

def analyze():
    conn = sqlite3.connect('d:/www/ReadRelint/data/relints.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT arquivo_origem, resumo, conteudo, metodo_extracao FROM relints")
    rows = c.fetchall()
    
    data = []
    for r in rows:
        data.append({
            "arquivo": r["arquivo_origem"],
            "metodo": r["metodo_extracao"],
            "resumo": r["resumo"],
            "conteudo_inicio": r["conteudo"][:1000] if r["conteudo"] else ""
        })
        
    with open('d:/www/ReadRelint/analysis_scratch.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    analyze()
