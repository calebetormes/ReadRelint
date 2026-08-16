import sqlite3

conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("--- RELINTS ---")
c.execute("SELECT id, source_file, subject FROM relints")
relints = c.fetchall()
for r in relints:
    print(dict(r))

print("\n--- PERSONS ---")
c.execute("SELECT * FROM persons")
persons = c.fetchall()
print(f"Total pessoas: {len(persons)}")
for p in persons:
    print(dict(p))

print("\n--- RELINT_PARTICIPANTS ---")
c.execute("SELECT * FROM relint_participants")
parts = c.fetchall()
print(f"Total participações: {len(parts)}")
for pt in parts:
    print(dict(pt))

conn.close()
