import re
import shutil
import sqlite3

ARQUIVO = "alunos.csv"

shutil.copy("crisma.db", "crisma_backup.db")

# Lê o arquivo (tenta UTF-8 e, se falhar, o padrão do Excel)
try:
    with open(ARQUIVO, encoding="utf-8-sig") as f:
        linhas = f.read().splitlines()
except UnicodeDecodeError:
    with open(ARQUIVO, encoding="cp1252") as f:
        linhas = f.read().splitlines()

padrao = re.compile(r"^(.*?),\s*Turma\s*(\d+)\s*$", re.IGNORECASE)

novos = []
vistos = set()

for linha in linhas:
    m = padrao.match(linha.strip())
    if not m:
        continue  # ignora títulos como "SANTO ANTÔNIO" e linhas vazias

    nome = " ".join(m.group(1).split())  # tira espaços sobrando
    turma_id = int(m.group(2))

    chave = (nome.lower(), turma_id)
    if chave in vistos:
        print(f"Repetido na mesma turma, ignorado: {nome} (turma {turma_id})")
        continue
    vistos.add(chave)

    novos.append((nome, turma_id))

conn = sqlite3.connect("crisma.db")
conn.execute("PRAGMA foreign_keys = ON")

ids_validos = {r[0] for r in conn.execute("SELECT id FROM turmas")}
invalidas = {t for _, t in novos} - ids_validos
if invalidas:
    print("Turmas que não existem no banco:", invalidas)
    conn.close()
    raise SystemExit

turmas_no_arquivo = sorted({t for _, t in novos})
for turma_id in turmas_no_arquivo:
    conn.execute("DELETE FROM alunos WHERE turma_id = ?", (turma_id,))

conn.executemany(
    "INSERT INTO alunos (nome, turma_id) VALUES (?, ?)",
    novos,
)

conn.commit()
conn.close()

for t in turmas_no_arquivo:
    print(f"Turma {t}: {sum(1 for _, x in novos if x == t)} alunos")
print(f"Pronto! {len(novos)} alunos importados.")