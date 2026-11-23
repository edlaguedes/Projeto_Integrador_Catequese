# Sistema de Gestão da Catequese

Sistema web desenvolvido para auxiliar na organização e no acompanhamento das atividades da catequese, facilitando o gerenciamento de turmas, catequizandos, chamadas e frequência.

O projeto busca substituir controles manuais por uma solução digital, tornando o acompanhamento dos participantes mais simples e organizado.

🎯 Objetivo do projeto

Desenvolver uma solução digital que facilite o gerenciamento das atividades da catequese, permitindo aos responsáveis organizar as turmas, registrar presenças e faltas e acompanhar a frequência dos catequizandos.

O projeto busca contribuir para a substituição de controles manuais, tornando o acompanhamento dos participantes mais prático e organizado.

🎓 Contexto academico

Instituição: Faculdade Senac.

Curso: Análise e Desenvolvimento de Sistemas (ADS).

Atividade: Projeto Integrador.

Tipo de projeto: Aplicação Web.

## ⚙️ Funcionalidades

- **Autenticação:** acesso ao sistema por meio de login.
- **Gerenciamento de turmas:** organização dos catequizandos em diferentes turmas.
- **Cadastro de catequizandos:** visualização e gerenciamento dos participantes.
- **Controle de presença:** registro de presenças e faltas por data.
- **Alertas de frequência:** identificação de catequizandos com três ou mais faltas.
- **Painel dos responsáveis:** acesso dos pais ou responsáveis às informações dos catequizandos.


## 🛠️ Tecnologias utilizadas

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript

## 🗂️ Estrutura do projeto

```text
Catequese/
│
├── static/
│   ├── chamada.css
│   ├── chamada.js
│   ├── image-removebg-preview.png
│   ├── pais.css
│   ├── style.css
│   ├── turmas.css
│
├── templates/
│   ├── chamada.html
│   ├── login_pais.html
│   ├── login.html
│   ├── painel_pais.html
│   ├── responsaveis.html
│   ├── turmas.html
│
├── alunos.csv
├── app.py
├── crisma_backup.db
├── crisma_original.db
├── crisma.db
├── importar_alunos.py
├── README.md
├── renomear_turmas.py
├── requirements.txt
└── trocar_alunos_csv.py
```

## ▶️ Como executar o projeto

**1. Clone o repositório**

```bash
git clone https://github.com/SEU-USUARIO/Catequese.git
```

**2. Acesse a pasta**

```bash
cd Catequese
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Configure a variável de ambiente**

Defina a chave secreta do Flask antes de executar a aplicação.

**5. Execute o sistema**

```bash
python app.py
```

Acesse pelo navegador:

```text
http://127.0.0.1:5000
```

## 📚 Aprendizados

O desenvolvimento deste projeto proporciona a aplicação prática de conhecimentos em:

- Desenvolvimento de aplicações web com Python e Flask.
- Integração entre aplicação e banco de dados SQLite.
- Operações CRUD.
- Autenticação e gerenciamento de sessões.
- Manipulação e importação de arquivos CSV.
- Organização e estruturação de projetos.

## 👩‍💻 Autora

Projeto acadêmico desenvolvido como parte do Projeto Integrador do curso de Análise e Desenvolvimento de Sistemas da Faculdade Senac.
