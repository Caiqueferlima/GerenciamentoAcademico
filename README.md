# 🎓 Sistema Acadêmico Desktop

Sistema desktop com autenticação e dois perfis (Professor / Aluno).
Desenvolvido em **Python + PySide6 + SQLAlchemy + SQLite**, com importação
de planilhas Excel e dashboards diferenciados por perfil.

## ✨ Funcionalidades

- Cadastro de usuários (Professor e Aluno) — HU01
- Login com validação de credenciais — HU02
- Área exclusiva do Professor com importação de planilha e estatísticas — HU03
- Área exclusiva do Aluno com dados individuais — HU04
- Encerramento de sessão (logout) — HU05

## 🗂️ Estrutura

```
database/     -> Models SQLAlchemy e sessão
controllers/  -> Regras de negócio (cadastro, login)
views/        -> Telas PySide6
utils/        -> Hash de senha e importador de planilhas
scripts/      -> Utilitários (gerador de planilha exemplo)
main.py       -> Ponto de entrada
```

## ⚙️ Como executar

1. **Clone e crie um ambiente virtual**

   ```bash
   git clone <url-do-seu-repo>
   cd sistema_academico
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

3. **Execute**

   ```bash
   python main.py
   ```

   O banco `sistema_academico.db` será criado automaticamente na primeira execução.

## 🧪 Testando

1. Rode `python scripts/gerar_planilha_exemplo.py` para gerar `alunos_exemplo.xlsx`.
2. Cadastre-se como **Professor** na tela inicial.
3. Faça login e clique em **Importar Planilha de Alunos**.
4. Faça logout e entre com um aluno importado
   (login = e-mail da planilha, **senha = matrícula**).

## 📐 Modelo Entidade-Relacionamento (MER)

Entidades: `Usuario`, `Aluno`, `Professor`, `Curso`, `Disciplina`, `Matricula`.

- `Usuario (1) ― (0..1) Aluno`
- `Usuario (1) ― (0..1) Professor`
- `Aluno (N) ― (1) Curso`
- `Aluno (N) ― (N) Disciplina` via `Matricula`

## 🔒 Segurança

- Senhas armazenadas com **bcrypt** (nunca em texto puro).
- Sessão encerrada explicitamente via botão *Encerrar sessão*.