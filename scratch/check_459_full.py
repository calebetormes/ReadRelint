import sqlite3
import json

conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT * FROM relints WHERE doc_id = 5")
row = dict(c.fetchone())

print("FULL ROW FOR DOC 5 (RELINT 459):")
for k, v in row.items():
    if k == 'data':
        try:
            parsed = json.loads(v)
            print("  data (JSON):", json.dumps(parsed, indent=2, ensure_ascii=False))
        except Exception as e:
            print("  data:", v)
    else:
        print(f"  {k}: {v}")
