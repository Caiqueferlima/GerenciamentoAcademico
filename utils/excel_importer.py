import pandas as pd
from database.db import get_session
from database.models import Usuario, Aluno, Curso, PerfilEnum
from utils.security import hash_senha


def _to_int(valor):
    try:
        if pd.isna(valor):
            return None
        return int(valor)
    except (ValueError, TypeError):
        return None


def importar_alunos(caminho_arquivo: str, curso_id: int | None = None):
    """
    Lê uma planilha Excel com colunas:
        matricula | nome | email | ano_ingresso | semestre_ingresso
    Cria Usuario + Aluno para cada linha.
    Senha inicial = matrícula (o aluno pode trocar depois).
    Retorna (inseridos, ignorados, erros).
    """
    df = pd.read_excel(caminho_arquivo, engine="openpyxl")

    colunas_obrigatorias = {"matricula", "nome", "email"}
    faltando = colunas_obrigatorias - set(df.columns)
    if faltando:
        raise ValueError(f"Colunas obrigatórias ausentes na planilha: {faltando}")

    session = get_session()
    inseridos = 0
    ignorados = 0
    erros = []

    try:
        # Garante que exista um curso padrão
        if curso_id is None:
            curso = session.query(Curso).first()
            if not curso:
                curso = Curso(nome="Curso Padrão", codigo="PADRAO")
                session.add(curso)
                session.flush()
            curso_id = curso.id

        for idx, linha in df.iterrows():
            try:
                matricula = str(linha["matricula"]).strip()
                nome = str(linha["nome"]).strip()
                email = str(linha["email"]).strip().lower()

                if not matricula or not nome or not email:
                    erros.append(f"Linha {idx + 2}: dados incompletos.")
                    continue

                if session.query(Aluno).filter_by(matricula=matricula).first():
                    ignorados += 1
                    continue
                if session.query(Usuario).filter_by(email=email).first():
                    ignorados += 1
                    continue

                usuario = Usuario(
                    nome=nome,
                    email=email,
                    senha_hash=hash_senha(matricula),  # senha inicial = matrícula
                    perfil=PerfilEnum.ALUNO,
                )
                session.add(usuario)
                session.flush()

                aluno = Aluno(
                    usuario_id=usuario.id,
                    matricula=matricula,
                    curso_id=curso_id,
                    ano_ingresso=_to_int(linha.get("ano_ingresso")),
                    semestre_ingresso=_to_int(linha.get("semestre_ingresso")),
                )
                session.add(aluno)
                inseridos += 1
            except Exception as e:
                erros.append(f"Linha {idx + 2}: {e}")

        session.commit()
    finally:
        session.close()

    return inseridos, ignorados, erros