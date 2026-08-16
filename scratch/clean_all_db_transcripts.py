import sys
sys.path.insert(0, '.')

import sqlite3
import json
from src.application.text_cleaner import normalize_whitespace_and_paragraphs

conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("Tables in DB:", tables)

if 'relints' in tables:
    c.execute("SELECT doc_id, source_file, data FROM relints")
    rows = c.fetchall()

    updated_count = 0
    for row in rows:
        doc_id = row['doc_id']
        data_str = row['data']
        if not data_str:
            continue
            
        try:
            data_obj = json.loads(data_str)
            raw_content = data_obj.get('content', '')
            if raw_content:
                cleaned_content = normalize_whitespace_and_paragraphs(raw_content)
                if cleaned_content != raw_content:
                    data_obj['content'] = cleaned_content
                    c.execute("UPDATE relints SET data = ? WHERE doc_id = ?", (json.dumps(data_obj, ensure_ascii=False), doc_id))
                    updated_count += 1
                    print(f"Updated doc_id {doc_id}: {row['source_file']}")
        except Exception as e:
            print(f"Error updating doc_id {doc_id}: {e}")

    conn.commit()
    print(f"Finished updating {updated_count} RELINT transcripts in database!")
