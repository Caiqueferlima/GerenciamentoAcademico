from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///sistema_academico.db"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_session():
    return SessionLocal()


def init_db():
    # Import necessário para registrar os modelos no metadata
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)