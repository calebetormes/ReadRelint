import sys
sys.path.insert(0, '.')

import sqlite3
import json

conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relints'")
if c.fetchone():
    c.execute("SELECT doc_id, data FROM relints")
    rows = c.fetchall()
    
    cleaned_count = 0
    for row in rows:
        doc_id = row['doc_id']
        data_str = row['data']
        if not data_str:
            continue
            
        try:
            data_obj = json.loads(data_str)
            modified = False
            
            # Remove campos descontinuados street e number
            if 'street' in data_obj:
                del data_obj['street']
                modified = True
            if 'number' in data_obj:
                del data_obj['number']
                modified = True
                
            if modified:
                c.execute("UPDATE relints SET data = ? WHERE doc_id = ?", (json.dumps(data_obj, ensure_ascii=False), doc_id))
                cleaned_count += 1
        except Exception as e:
            print(f"Error optimizing row {doc_id}: {e}")
            
    conn.commit()
    print(f"Otimizados {cleaned_count} registros removendo redundâncias do JSON.")

# Executa VACUUM para desfragmentar e reduzir tamanho do banco em disco
c.execute("VACUUM;")
conn.close()
print("Banco de dados otimizado e desfragmentado via VACUUM com sucesso!")
