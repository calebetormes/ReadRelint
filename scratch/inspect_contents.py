import sys
sys.path.insert(0, '.')

import sqlite3
import json

conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT doc_id, source_file, data FROM relints")
rows = c.fetchall()

for row in rows:
    doc_id = row['doc_id']
    data_str = row['data']
    if data_str:
        data_obj = json.loads(data_str)
        content_preview = data_obj.get('content', '')[:150]
        print(f"Doc {doc_id} ({row['source_file']}):")
        print(f"  Content preview: {repr(content_preview)}")
        print("-" * 50)
