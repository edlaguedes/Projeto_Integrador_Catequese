import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "crisma.db"
CSV_PATH = BASE_DIR / "alunos.csv"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as arquivo:

    leitor = csv.DictReader(arquivo)

    print("Colunas encontradas:", leitor.fieldnames)

    for linha in leitor:

        # Aceita Nome/nome e Turma/turma
        nome = linha["Nome"].strip()
        nome_turma = linha["Turma"].strip()

        # Procura a turma ignorando maiúsculas/minúsculas
        turma = cursor.execute(
            """
            SELECT id
            FROM turmas
            WHERE LOWER(nome) = LOWER(?)
            """,
            (nome_turma,)
        ).fetchone()

        if turma is None:
            print(f"Turma não encontrada: {nome_turma}")
            continue

        turma_id = turma[0]

        # Verifica se o aluno já existe nessa turma
        existe = cursor.execute(
            """
            SELECT id
            FROM alunos
            WHERE LOWER(nome) = LOWER(?)
              AND turma_id = ?
            """,
            (nome, turma_id)
        ).fetchone()

        if existe:
            print(f"Já existe: {nome} - {nome_turma}")
            continue

        # Adiciona o aluno
        cursor.execute(
            """
            INSERT INTO alunos (nome, turma_id)
            VALUES (?, ?)
            """,
            (nome, turma_id)
        )

        print(f"Adicionado: {nome} - {nome_turma}")

conn.commit()
conn.close()

print("\nImportação concluída!")