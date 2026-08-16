import sqlite3

conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT doc_id, source_file, subject, bm_group, relint_type, summary FROM relints")
rows = c.fetchall()

print(f"Total rows: {len(rows)}")
for r in rows:
    if '459' in str(r['doc_id']) or '459' in str(r['source_file']):
        print("MATCH 459:")
        print(dict(r))
    else:
        print(f"Doc: {r['doc_id']} | File: {r['source_file']} | Subject: {r['subject']}")
