from database.db import get_session
from database.models import Usuario, Aluno, Professor, PerfilEnum
from utils.security import hash_senha, verificar_senha


def cadastrar_usuario(nome, email, senha, perfil,
                      matricula=None, ano=None, semestre=None,
                      departamento=None):
    """Cadastra um novo usuário (Professor ou Aluno)."""
    session = get_session()
    try:
        if session.query(Usuario).filter_by(email=email.lower()).first():
            return None, "Este e-mail já está cadastrado."

        usuario = Usuario(
            nome=nome.strip(),
            email=email.strip().lower(),
            senha_hash=hash_senha(senha),
            perfil=PerfilEnum(perfil),
        )
        session.add(usuario)
        session.flush()

        if perfil == "ALUNO":
            if not matricula:
                session.rollback()
                return None, "Matrícula é obrigatória para alunos."
            if session.query(Aluno).filter_by(matricula=matricula).first():
                session.rollback()
                return None, "Esta matrícula já está cadastrada."
            aluno = Aluno(
                usuario_id=usuario.id,
                matricula=matricula.strip(),
                ano_ingresso=ano,
                semestre_ingresso=semestre,
            )
            session.add(aluno)
        elif perfil == "PROFESSOR":
            prof = Professor(usuario_id=usuario.id, departamento=departamento)
            session.add(prof)
        else:
            session.rollback()
            return None, "Perfil inválido."

        session.commit()
        return usuario.id, None
    except Exception as e:
        session.rollback()
        return None, f"Erro ao cadastrar: {e}"
    finally:
        session.close()


def autenticar(email: str, senha: str):
    """Retorna (dict_usuario, None) em caso de sucesso ou (None, msg_erro)."""
    session = get_session()
    try:
        usuario = session.query(Usuario).filter_by(email=email.strip().lower()).first()
        if not usuario:
            return None, "Usuário não encontrado."
        if not verificar_senha(senha, usuario.senha_hash):
            return None, "Senha incorreta."

        return {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil.value,
        }, None
    finally:
        session.close()