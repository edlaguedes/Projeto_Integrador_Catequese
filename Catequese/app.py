import os
import sqlite3

from pathlib import Path
from datetime import date
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# =========================================================
# CONFIGURAÇÃO
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "crisma.db"

app = Flask(__name__)



# =========================================================
# CHAVE SECRETA
# =========================================================

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "FLASK_SECRET_KEY não foi configurada."
    )

app.secret_key = SECRET_KEY



# =========================================================
# CONFIGURAÇÕES DE SEGURANÇA DA SESSÃO
# =========================================================

app.config.update(
SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
    TRUSTED_HOSTS=os.environ.get(
        "TRUSTED_HOSTS", "127.0.0.1,localhost"
    ).split(",")
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# =========================================================
# CABEÇALHOS DE SEGURANÇA
# =========================================================

@app.after_request
def adicionar_cabecalhos_seguranca(response):

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    response.headers["Permissions-Policy"] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=()"
    )

    if request.is_secure:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


# =========================================================
# BANCO DE DADOS
# =========================================================

def get_db():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# =========================================================
# INICIALIZAÇÃO DO BANCO
# =========================================================

def init_db():

    conn = get_db()

    conn.executescript("""

        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            turma_id INTEGER NOT NULL,

            FOREIGN KEY (turma_id)
            REFERENCES turmas(id)
            ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS chamadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            aluno_id INTEGER NOT NULL,

            data TEXT NOT NULL,

            presente INTEGER NOT NULL
            CHECK (presente IN (0, 1)),

            UNIQUE(aluno_id, data),

            FOREIGN KEY (aluno_id)
            REFERENCES alunos(id)
            ON DELETE CASCADE

        );
                CREATE TABLE IF NOT EXISTS responsaveis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS responsavel_alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            responsavel_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,

            UNIQUE(responsavel_id, aluno_id),

            FOREIGN KEY (responsavel_id)
                REFERENCES responsaveis(id)
                ON DELETE CASCADE,

            FOREIGN KEY (aluno_id)
                REFERENCES alunos(id)
                ON DELETE CASCADE
        );

    """)

    # =====================================================
    # USUÁRIO ADMINISTRADOR
    # =====================================================

    usuario = conn.execute(
        "SELECT id FROM usuarios LIMIT 1"
    ).fetchone()

    if usuario is None:

        senha_admin = os.environ.get("CRISMA_ADMIN_PASSWORD")

        if not senha_admin:
            senha_admin = "123456"

            print(
                "ATENÇÃO: usando senha inicial 123456. "
                "Troque essa senha imediatamente."
            )

        conn.execute(
            """
            INSERT INTO usuarios
            (nome, email, senha)
            VALUES (?, ?, ?)
            """,
            (
                "Administrador",
                "admin@crisma.com",
                generate_password_hash(senha_admin)
            )
        )

    # =====================================================
    # TURMAS
    # =====================================================

    quantidade_turmas = conn.execute(
        "SELECT COUNT(*) FROM turmas"
    ).fetchone()[0]

    if quantidade_turmas == 0:

        nomes_turmas = [
            "São Francisco",
            "Santo Antônio",
            "São Miguel",
            "São José",
            "Santa Luzia",
            "Santa Rosa"
        ]

        for nome_turma in nomes_turmas:

            conn.execute(
                """
                INSERT INTO turmas (nome)
                VALUES (?)
                """,
                (nome_turma,)
            )

    conn.commit()

    conn.close()


# =========================================================
# LOGIN OBRIGATÓRIO
# =========================================================

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "usuario_id" not in session:

            return redirect(
                url_for("login")
            )

        return view(*args, **kwargs)

    return wrapped

# =========================================================
# LOGIN OBRIGATÓRIO DOS RESPONSÁVEIS
# =========================================================

def responsavel_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "responsavel_id" not in session:

            return redirect(
                url_for("login_pais")
            )

        return view(*args, **kwargs)

    return wrapped


# =========================================================
# PÁGINA INICIAL
# =========================================================

@app.route("/")
def index():

    if "usuario_id" in session:

        return redirect(
            url_for("turmas")
        )

    return redirect(
        url_for("login")
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    erro = None

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "senha",
            ""
        )

        if not email or not senha:

            erro = "Preencha o e-mail e a senha."

            return render_template(
                "login.html",
                erro=erro
            )

        conn = get_db()

        usuario = conn.execute(
            """
            SELECT *
            FROM usuarios
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()

        if usuario and check_password_hash(
            usuario["senha"],
            senha
        ):

            session.clear()

            session["usuario_id"] = usuario["id"]

            session["usuario_nome"] = usuario["nome"]

            return redirect(
                url_for("turmas")
            )

        erro = "E-mail ou senha inválidos."

    return render_template(
        "login.html",
        erro=erro
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# TURMAS
# =========================================================

@app.route("/turmas")
@login_required
def turmas():

    conn = get_db()

    lista = conn.execute(
        """
        SELECT *
        FROM turmas
        ORDER BY id
        """
    ).fetchall()

    conn.close()

    return render_template(
        "turmas.html",
        turmas=lista
    )


# =========================================================
# CHAMADA
# =========================================================

@app.route("/turma/<int:turma_id>")
@login_required
def chamada(turma_id):

    conn = get_db()

    turma = conn.execute(
        """
        SELECT *
        FROM turmas
        WHERE id = ?
        """,
        (turma_id,)
    ).fetchone()

    if turma is None:

        conn.close()

        return "Turma não encontrada.", 404

    alunos = conn.execute(
        """
        SELECT *
        FROM alunos
        WHERE turma_id = ?
        ORDER BY nome
        """,
        (turma_id,)
    ).fetchall()

    # =====================================================
    # 52 DIAS
    # =====================================================

    dias = [
        date(2026, 10, 17),
        date(2026, 11, 7),
        date(2026, 11, 14),
        date(2026, 11, 28),
        date(2026, 12, 5),
        date(2027, 2, 13),
        date(2027, 2, 20),
        date(2027, 2, 27),
        date(2027, 3, 13),
        date(2027, 3, 20),
        date(2027, 4, 3),
        date(2027, 4, 10),
        date(2027, 4, 17),
        date(2027, 5, 8),
        date(2027, 5, 15),
        date(2027, 5, 22),
        date(2027, 5, 29),
        date(2027, 6, 5),
        date(2027, 6, 12),
        date(2027, 8, 1),
        date(2027, 8, 8),
        date(2027, 8, 21),
        date(2027, 9, 11),
        date(2027, 9, 18),
        date(2027, 9, 25),
        date(2027, 10, 2),
        date(2027, 10, 9),
        date(2027, 10, 16),
        date(2027, 10, 23),
        date(2027, 11, 6),
        date(2027, 11, 27),
        date(2027, 12, 4),
        date(2027, 12, 11),
        date(2028, 2, 5),
        date(2028, 2, 12),
        date(2028, 2, 19),
        date(2028, 3, 4),
        date(2028, 3, 11),
        date(2028, 3, 18),
        date(2028, 3, 25),
        date(2028, 4, 1),
        date(2028, 4, 8),
        date(2028, 5, 6),
        date(2028, 5, 13),
        date(2028, 5, 20),
        date(2028, 5, 27),
    ]

    # =====================================================
    # MÊS SELECIONADO
    # =====================================================

    dias = sorted(dias)

    meses = sorted({(d.year, d.month) for d in dias})

    hoje = date.today()
    futuros = [m for m in meses if m >= (hoje.year, hoje.month)]
    selecionado = futuros[0] if futuros else meses[-1]

    mes_param = request.args.get("mes", "")

    try:
        ano_p, mes_p = map(int, mes_param.split("-"))
        if (ano_p, mes_p) in meses:
            selecionado = (ano_p, mes_p)
    except ValueError:
        pass

    dias_mes = [
        d for d in dias
        if (d.year, d.month) == selecionado
    ]

    meses_nav = [
        {
            "valor": f"{a}-{m:02d}",
            "rotulo": f"{MESES_PT[m - 1]}/{a}",
            "ativo": (a, m) == selecionado,
        }
        for a, m in meses
    ]

  

    # =====================================================
    # REGISTROS
    # =====================================================

    registros = conn.execute(
        """
        SELECT
            c.aluno_id,
            c.data,
            c.presente

        FROM chamadas c

        JOIN alunos a
            ON a.id = c.aluno_id

        WHERE a.turma_id = ?
        """,
        (turma_id,)
    ).fetchall()

    conn.close()

    # =====================================================
    # MAPA DE PRESENÇA
    # =====================================================

    mapa = {
        (
            registro["aluno_id"],
            registro["data"]
        ): bool(registro["presente"])

        for registro in registros
    }

    # =====================================================
    # DADOS DOS ALUNOS
    # =====================================================

    dados = []

    for aluno in alunos:

        faltas = sum(
            1
            for dia in dias
            if mapa.get(
                (
                    aluno["id"],
                    dia.isoformat()
                )
            ) is False
        )

        dados.append({

            "id": aluno["id"],

            "nome": aluno["nome"],

            "faltas": faltas,

            "status":
                "Alerta"
                if faltas >= 3
                else "Normal"

        })

        
    return render_template(
          "chamada.html",
  
          turma=turma,
  
          alunos=dados,
  
          dias=dias_mes,
          todos_dias=dias,
          meses=meses_nav,
  
          mapa=mapa
  )   
  

# =========================================================
# REGISTRAR CHAMADA
# =========================================================

@app.post("/api/chamada")
@login_required
def registrar_chamada():

    # =====================================================
    # RECEBE JSON
    # =====================================================

    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):

        return jsonify({
            "ok": False,
            "erro": "Dados inválidos."
        }), 400

    # =====================================================
    # DADOS
    # =====================================================

    aluno_id = data.get("aluno_id")

    data_aula = data.get("data")

    presente = data.get("presente")

    # =====================================================
    # VALIDA ALUNO
    # =====================================================

    if aluno_id is None:

        return jsonify({
            "ok": False,
            "erro": "Aluno não informado."
        }), 400

    try:

        aluno_id = int(aluno_id)

    except (ValueError, TypeError):

        return jsonify({
            "ok": False,
            "erro": "Aluno inválido."
        }), 400

    # =====================================================
    # VALIDA DATA
    # =====================================================

    if not data_aula:

        return jsonify({
            "ok": False,
            "erro": "Data não informada."
        }), 400

    try:

        date.fromisoformat(data_aula)

    except ValueError:

        return jsonify({
            "ok": False,
            "erro": "Data inválida."
        }), 400

    # =====================================================
    # VALIDA PRESENTE
    # =====================================================

    if presente not in (
        True,
        False,
        None
    ):

        return jsonify({
            "ok": False,
            "erro": "Valor de presença inválido."
        }), 400

    conn = get_db()

    # =====================================================
    # VERIFICA ALUNO
    # =====================================================

    aluno = conn.execute(
        """
        SELECT id
        FROM alunos
        WHERE id = ?
        """,
        (aluno_id,)
    ).fetchone()

    if aluno is None:

        conn.close()

        return jsonify({
            "ok": False,
            "erro": "Aluno não encontrado."
        }), 404

    # =====================================================
    # RETIRAR MARCAÇÃO
    # =====================================================

    if presente is None:

        conn.execute(
            """
            DELETE FROM chamadas

            WHERE aluno_id = ?

            AND data = ?
            """,
            (
                aluno_id,
                data_aula
            )
        )

    # =====================================================
    # PRESENTE OU FALTA
    # =====================================================

    else:

        conn.execute(
            """
            INSERT INTO chamadas
            (
                aluno_id,
                data,
                presente
            )

            VALUES (?, ?, ?)

            ON CONFLICT(aluno_id, data)

            DO UPDATE SET
                presente = excluded.presente
            """,
            (
                aluno_id,
                data_aula,
                int(presente)
            )
        )

    conn.commit()

    # =====================================================
    # CALCULA FALTAS
    # =====================================================

    faltas = conn.execute(
        """
        SELECT COUNT(*)

        FROM chamadas

        WHERE aluno_id = ?

        AND presente = 0
        """,
        (aluno_id,)
    ).fetchone()[0]

    conn.close()

    # =====================================================
    # RESPOSTA
    # =====================================================

    return jsonify({

        "ok": True,

        "faltas": faltas,

        "status":
            "Alerta"
            if faltas >= 3
            else "Normal"

    })


# =========================================================
# CADASTRO DE RESPONSÁVEIS
# =========================================================

@app.route("/responsaveis", methods=["GET", "POST"])
@login_required
def responsaveis():

    conn = get_db()

    erro = None
    sucesso = None

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        alunos_ids = request.form.getlist("alunos")

        if not nome or not email or not senha:
            erro = "Preencha todos os campos."

        elif len(senha) < 8:
            erro = "A senha precisa ter pelo menos 8 caracteres."

        elif not alunos_ids:
            erro = "Selecione pelo menos um catequizando."

        else:

            try:

                ids = list(set(int(i) for i in alunos_ids))

                placeholders = ",".join("?" for _ in ids)

                alunos_validos = conn.execute(
                    f"""
                    SELECT id
                    FROM alunos
                    WHERE id IN ({placeholders})
                    """,
                    ids
                ).fetchall()

                if len(alunos_validos) != len(ids):

                    erro = "Seleção de alunos inválida."

                else:

                    cursor = conn.execute(
                        """
                        INSERT INTO responsaveis
                        (nome, email, senha)
                        VALUES (?, ?, ?)
                        """,
                        (
                            nome,
                            email,
                            generate_password_hash(senha)
                        )
                    )

                    responsavel_id = cursor.lastrowid

                    for aluno_id in ids:

                        conn.execute(
                            """
                            INSERT INTO responsavel_alunos
                            (responsavel_id, aluno_id)
                            VALUES (?, ?)
                            """,
                            (responsavel_id, aluno_id)
                        )

                    conn.commit()

                    sucesso = "Responsável cadastrado com sucesso!"

            except ValueError:

                conn.rollback()
                erro = "Seleção de alunos inválida."

            except sqlite3.IntegrityError:

                conn.rollback()
                erro = "Este e-mail já está cadastrado."

    alunos = conn.execute(
        """
        SELECT
            a.id,
            a.nome,
            t.nome AS turma

        FROM alunos a

        JOIN turmas t
            ON t.id = a.turma_id

        ORDER BY a.nome
        """
    ).fetchall()

    lista = conn.execute(
        """
        SELECT
            r.id,
            r.nome,
            r.email,
            GROUP_CONCAT(a.nome, ', ') AS filhos

        FROM responsaveis r

        LEFT JOIN responsavel_alunos ra
            ON ra.responsavel_id = r.id

        LEFT JOIN alunos a
            ON a.id = ra.aluno_id

        GROUP BY r.id

        ORDER BY r.nome
        """
    ).fetchall()

    conn.close()

    return render_template(
        "responsaveis.html",
        alunos=alunos,
        responsaveis=lista,
        erro=erro,
        sucesso=sucesso
    )
# =========================================================
# LOGIN DOS RESPONSÁVEIS
# =========================================================

@app.route("/pais/login", methods=["GET", "POST"])
def login_pais():

    erro = None

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        senha = request.form.get("senha", "")

        conn = get_db()

        responsavel = conn.execute(
            """
            SELECT *
            FROM responsaveis
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()

        if responsavel and check_password_hash(
            responsavel["senha"], senha
        ):

            session.clear()

            session["responsavel_id"] = responsavel["id"]
            session["responsavel_nome"] = responsavel["nome"]

            return redirect(
                url_for("painel_pais")
            )

        erro = "E-mail ou senha inválidos."

    return render_template(
        "login_pais.html",
        erro=erro
    )

# =========================================================
# PAINEL DOS RESPONSÁVEIS
# =========================================================

@app.route("/pais")
@responsavel_required
def painel_pais():

    conn = get_db()

    filhos = conn.execute(
        """
        SELECT
            a.id,
            a.nome,
            t.nome AS turma

        FROM responsavel_alunos ra

        JOIN alunos a
            ON a.id = ra.aluno_id

        JOIN turmas t
            ON t.id = a.turma_id

        WHERE ra.responsavel_id = ?

        ORDER BY a.nome
        """,
        (session["responsavel_id"],)
    ).fetchall()

    dados_filhos = []

    for filho in filhos:

        registros = conn.execute(
            """
            SELECT data, presente
            FROM chamadas
            WHERE aluno_id = ?
            ORDER BY data DESC
            """,
            (filho["id"],)
        ).fetchall()

        total = len(registros)

        presencas = sum(
            1 for r in registros
            if r["presente"] == 1
        )

        faltas = sum(
            1 for r in registros
            if r["presente"] == 0
        )

        percentual = (
            round(presencas / total * 100, 1)
            if total else 0
        )

        historico = []

        for registro in registros[:10]:

            historico.append({
                "data": date.fromisoformat(
                    registro["data"]
                ).strftime("%d/%m/%Y"),

                "status": (
                    "Presente"
                    if registro["presente"] == 1
                    else "Falta"
                )
})

        dados_filhos.append({

            "id": filho["id"],
            "nome": filho["nome"],
            "turma": filho["turma"],
            "presencas": presencas,
            "faltas": faltas,
            "percentual": percentual,
            "historico": historico

        })

    conn.close()

    return render_template(
    "painel_pais.html",
    responsavel_nome=session["responsavel_nome"],
    alunos=dados_filhos
)
# =========================================================
# SAIR DA ÁREA DOS PAIS
# =========================================================

@app.route("/pais/sair")
@responsavel_required
def logout_pais():

    session.clear()

    return redirect(
        url_for("login_pais")
    )

# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    init_db()
    
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
