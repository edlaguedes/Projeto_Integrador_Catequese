import shutil
import sqlite3

# Backup de segurança
shutil.copy("crisma.db", "crisma_backup.db")

novos_nomes = {
    1: "São Francisco",
    2: "Santo Antônio",
    3: "São Miguel",
    4: "São José",
    5: "Santa Luzia",
    6: "Santa Rosa",
}

conn = sqlite3.connect("crisma.db")

for turma_id, nome in novos_nomes.items():
    conn.execute(
        "UPDATE turmas SET nome = ? WHERE id = ?",
        (nome, turma_id),
    )

conn.commit()
conn.close()

