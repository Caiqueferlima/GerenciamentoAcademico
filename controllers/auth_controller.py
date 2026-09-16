from database.db import get_session
from database.models import Usuario, Professor, PerfilEnum
from utils.security import hash_senha, verificar_senha


def cadastrar_usuario(nome, email, senha, siape):
    """Cadastra um novo professor."""
    session = get_session()
    try:
        login = email.strip().lower()
        if session.query(Usuario).filter_by(login=login).first():
            return None, "Este e-mail já está cadastrado."

        usuario = Usuario(
            nome=nome.strip(),
            login=login,
            senha_hash=hash_senha(senha),
            perfil=PerfilEnum.PROFESSOR,
        )
        session.add(usuario)
        session.flush()

        if not siape or not siape.strip():
            session.rollback()
            return None, "Número de SIAPE é obrigatório."
        if session.query(Professor).filter_by(siape=siape.strip()).first():
            session.rollback()
            return None, "Este número de SIAPE já está cadastrado."
        session.add(Professor(usuario_id=usuario.id, siape=siape.strip()))

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
        usuario = session.query(Usuario).filter_by(login=email.strip().lower()).first()
        if not usuario:
            return None, "Usuário não encontrado."
        if not verificar_senha(senha, usuario.senha_hash):
            return None, "Senha incorreta."

        return {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.login,
            "perfil": usuario.perfil.value,
        }, None
    finally:
        session.close()