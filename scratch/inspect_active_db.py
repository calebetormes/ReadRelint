import sqlite3

conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT id, source_file, subject FROM relints")
relints = c.fetchall()
print(f"--- RELINTS ({len(relints)} registros) ---")
for r in relints:
    print(f"ID {r['id']}: {r['source_file']}")

c.execute("SELECT * FROM persons")
persons = c.fetchall()
print(f"\n--- PERSONS ({len(persons)} registros) ---")
for p in persons:
    print(dict(p))

c.execute("SELECT * FROM relint_participants")
parts = c.fetchall()
print(f"\n--- RELINT_PARTICIPANTS ({len(parts)} registros) ---")
for pt in parts:
    print(dict(pt))

conn.close()
