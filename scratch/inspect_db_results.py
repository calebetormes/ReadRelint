import sqlite3

conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT COUNT(*) as cnt FROM relints")
print(f"Total na tabela 'relints': {c.fetchone()['cnt']}")

c.execute("SELECT COUNT(*) as cnt FROM persons")
print(f"Total na tabela 'persons': {c.fetchone()['cnt']}")

c.execute("SELECT COUNT(*) as cnt FROM relint_participants")
print(f"Total na tabela 'relint_participants': {c.fetchone()['cnt']}")

print("\n--- PESSOAS CADASTRADAS NAS TABELAS RELACIONAIS ---")
c.execute("SELECT id, person_key, name, nickname, document FROM persons")
persons = c.fetchall()
for pr in persons:
    print(f" - ID {pr['id']} | Nome: {pr['name']} | Vulgo: {pr['nickname']} | Doc: {pr['document']}")

print("\n--- LIGAÇÃO RELINT <-> PERSON (relint_participants) ---")
c.execute("""
    SELECT rp.id, p.name, rp.participation_type, r.source_file
    FROM relint_participants rp
    JOIN persons p ON rp.person_id = p.id
    JOIN relints r ON rp.relint_id = r.id
""")
parts = c.fetchall()
for pt in parts:
    print(f" - {pt['name']} ({pt['participation_type']}) -> {pt['source_file']}")

conn.close()
