import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database.db import Base


class PerfilEnum(str, enum.Enum):
    PROFESSOR = "PROFESSOR"
    ALUNO = "ALUNO"


class SexoEnum(str, enum.Enum):
    M = "M"
    F = "F"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    login = Column(String(120), unique=True, nullable=False, index=True)
    senha_hash = Column(String(200), nullable=False)
    nome = Column(String(150), nullable=False)
    perfil = Column(Enum(PerfilEnum), nullable=False)
    precisa_trocar_senha = Column(Boolean, default=False, nullable=False)

    aluno = relationship("Aluno", back_populates="usuario",
                         uselist=False, cascade="all, delete-orphan")
    professor = relationship("Professor", back_populates="usuario",
                             uselist=False, cascade="all, delete-orphan")


class Curso(Base):
    __tablename__ = "cursos"

    codigo = Column(String(10), primary_key=True)   # "03500"
    nome = Column(String(150), nullable=False)

    alunos = relationship("Aluno", back_populates="curso")
    disciplinas = relationship("Disciplina", back_populates="curso")


class Aluno(Base):
    __tablename__ = "alunos"

    matricula = Column(String(14), primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"),
                        unique=True, nullable=True)
    nome = Column(String(150), nullable=False)
    sexo = Column(Enum(SexoEnum))
    curso_codigo = Column(String(10), ForeignKey("cursos.codigo"))
    periodo_ingresso = Column(String(7))             # "2023/1"

    # Estado acadêmico atual
    situacao_matricula = Column(String(40), index=True)
    sit_ult_periodo_letivo = Column(String(40))
    turno = Column(String(30))
    turno_ingresso = Column(String(30))
    qtd_periodos = Column(Integer)
    tipo_forma_ingresso = Column(String(60))

    # Socioeconômico
    escola_origem = Column(String(150))
    area_procedencia = Column(String(80))
    agrupamento = Column(String(80))
    renda_familiar = Column(String(60))
    renda_familiar_per_capita = Column(String(60))

    importado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    usuario = relationship("Usuario", back_populates="aluno")
    curso = relationship("Curso", back_populates="alunos")
    conclusao = relationship("Conclusao", back_populates="aluno",
                             uselist=False, cascade="all, delete-orphan")
    pendencias = relationship("Pendencia", back_populates="aluno",
                              cascade="all, delete-orphan")


class Professor(Base):
    __tablename__ = "professores"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"),
                        unique=True, nullable=False)
    departamento = Column(String(80))

    usuario = relationship("Usuario", back_populates="professor")


class Conclusao(Base):
    __tablename__ = "conclusoes"

    matricula = Column(String(14), ForeignKey("alunos.matricula"),
                       primary_key=True)

    pct_cr_cumprido = Column(Integer)
    pct_cumprido = Column(Integer)

    ch_obrigatoria_cumpr = Column(Integer)
    ch_obrigatoria_prev = Column(Integer)
    ch_optativa_cumpr = Column(Integer)
    ch_optativa_prev = Column(Integer)
    ch_eletiva_cumpr = Column(Integer)
    ch_eletiva_prev = Column(Integer)
    ch_estagio_cumpr = Column(Integer)
    ch_estagio_prev = Column(Integer)
    ch_complementar_cumpr = Column(Integer)
    ch_complementar_prev = Column(Integer)
    ch_projeto_cumpr = Column(Integer)
    ch_projeto_prev = Column(Integer)
    ch_cumprida = Column(Integer)
    ch_prevista = Column(Integer)

    cr_cumpr = Column(Integer)
    cr_prev = Column(Integer)
    cr_obrigatorio_cumpr = Column(Integer)
    cr_obrigatorio_prev = Column(Integer)
    cr_optativo_cumpr = Column(Integer)
    cr_optativo_prev = Column(Integer)

    ano_conclusao_grad = Column(Integer)
    ano_conclusao_pos = Column(Integer)

    importado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    aluno = relationship("Aluno", back_populates="conclusao")


class Disciplina(Base):
    __tablename__ = "disciplinas"

    sigla = Column(String(20), primary_key=True)    # "3500.45"
    nome = Column(String(200), nullable=False)
    curso_codigo = Column(String(10), ForeignKey("cursos.codigo"))

    curso = relationship("Curso", back_populates="disciplinas")
    pendencias = relationship("Pendencia", back_populates="disciplina")


class Pendencia(Base):
    __tablename__ = "pendencias"
    __table_args__ = (
        UniqueConstraint("matricula", "disciplina_sigla", name="uq_pendencia"),
    )

    id = Column(Integer, primary_key=True)
    matricula = Column(String(14), ForeignKey("alunos.matricula"),
                       nullable=False, index=True)
    disciplina_sigla = Column(String(20), ForeignKey("disciplinas.sigla"),
                              nullable=False)
    importado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    aluno = relationship("Aluno", back_populates="pendencias")
    disciplina = relationship("Disciplina", back_populates="pendencias")