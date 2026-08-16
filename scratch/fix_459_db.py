import sys
sys.path.insert(0, '.')

import sqlite3
import json
from src.application.text_cleaner import extract_subject_fallback, extract_fallback_summary
from src.application.bm_classifier import classify_bm_group

conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT * FROM relints WHERE doc_id = 5")
row = dict(c.fetchone())

filename = row['source_file']
data_obj = json.loads(row['data'])
content = data_obj.get('content', '')

# Extract subject using new fallback
new_subject = extract_subject_fallback(content, filename)
new_summary = extract_fallback_summary(content, subject=new_subject)
new_bm_group = classify_bm_group(filename=filename, subject=new_subject, content=content)

print("NEW SUBJECT:", new_subject)
print("NEW SUMMARY:", new_summary)
print("NEW BM GROUP:", new_bm_group)

# Update database
data_obj['subject'] = new_subject
data_obj['summary'] = new_summary
data_obj['bm_group'] = new_bm_group

c.execute("""
    UPDATE relints 
    SET subject = ?, summary = ?, bm_group = ?, data = ?
    WHERE doc_id = 5
""", (new_subject, new_summary, new_bm_group, json.dumps(data_obj, ensure_ascii=False)))

conn.commit()
print("Successfully updated RELINT 459 in database!")
