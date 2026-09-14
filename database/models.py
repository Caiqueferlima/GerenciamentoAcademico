import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Float, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from database.db import Base


class PerfilEnum(str, enum.Enum):
    PROFESSOR = "PROFESSOR"
    ALUNO = "ALUNO"


class TipoDisciplinaEnum(str, enum.Enum):
    OBRIGATORIA = "OBRIGATORIA"
    OPTATIVA = "OPTATIVA"


class SituacaoEnum(str, enum.Enum):
    APROVADO = "APROVADO"
    REPROVADO = "REPROVADO"
    CURSANDO = "CURSANDO"
    PENDENTE = "PENDENTE"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    senha_hash = Column(String(200), nullable=False)
    perfil = Column(Enum(PerfilEnum), nullable=False)

    aluno = relationship(
        "Aluno", back_populates="usuario", uselist=False,
        cascade="all, delete-orphan"
    )
    professor = relationship(
        "Professor", back_populates="usuario", uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Usuario {self.email} ({self.perfil.value})>"


class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    matricula = Column(String(20), unique=True, nullable=False, index=True)
    curso_id = Column(Integer, ForeignKey("cursos.id"))
    ano_ingresso = Column(Integer)
    semestre_ingresso = Column(Integer)
    horas_complementares_ok = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="aluno")
    curso = relationship("Curso", back_populates="alunos")
    matriculas = relationship(
        "Matricula", back_populates="aluno", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Aluno {self.matricula} - {self.usuario.nome if self.usuario else ''}>"


class Professor(Base):
    __tablename__ = "professores"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    departamento = Column(String(80))

    usuario = relationship("Usuario", back_populates="professor")


class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    codigo = Column(String(20), unique=True)

    alunos = relationship("Aluno", back_populates="curso")


class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    codigo = Column(String(20), unique=True)
    carga_horaria = Column(Integer)
    tipo = Column(Enum(TipoDisciplinaEnum), default=TipoDisciplinaEnum.OBRIGATORIA)


class Matricula(Base):
    __tablename__ = "matriculas"

    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)
    ano = Column(Integer)
    semestre = Column(Integer)
    nota_final = Column(Float)
    situacao = Column(Enum(SituacaoEnum), default=SituacaoEnum.PENDENTE)

    aluno = relationship("Aluno", back_populates="matriculas")
    disciplina = relationship("Disciplina")