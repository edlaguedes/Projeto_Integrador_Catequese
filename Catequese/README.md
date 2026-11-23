# CRISMA - Sistema de Controle de Frequência

## 1. Requisitos

- Python 3.10 ou superior
- VS Code (recomendado)

## 2. Instalação

Abra o terminal dentro da pasta do projeto:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## 3. Executar

```bash
python app.py
```

Depois abra:

http://127.0.0.1:5000

## 4. Login inicial

E-mail:

admin@crisma.com

Senha:

123456

## 5. Funcionamento

Login -> Turmas -> Chamada.

Os registros de presença/falta são gravados no SQLite (`crisma.db`).

A tabela de chamada é gerada pelo Python. Os 52 dias não precisam ser escritos manualmente no HTML.

Ao registrar 3 ou mais faltas, o aluno passa automaticamente para "Alerta".

## 6. Banco SQL

O arquivo `banco.sql` contém a estrutura SQL. O `app.py` também cria automaticamente as tabelas na primeira execução.

## 7. Observação

O projeto usa SQLite para facilitar a instalação e os testes locais. Para colocar o sistema em produção, recomenda-se trocar a `secret_key`, remover as credenciais de demonstração e considerar PostgreSQL.
