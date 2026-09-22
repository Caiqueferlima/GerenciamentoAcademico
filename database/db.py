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
    with engine.begin() as connection:
        for table_name, column_name in (
            ("usuarios", "precisa_trocar_senha"),
            ("professores", "departamento"),
        ):
            columns = connection.exec_driver_sql(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
            if any(column[1] == column_name for column in columns):
                connection.exec_driver_sql(
                    f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
                )

        columns = connection.exec_driver_sql(
            "PRAGMA table_info(professores)"
        ).fetchall()
        if columns and not any(column[1] == "siape" for column in columns):
            connection.exec_driver_sql(
                "ALTER TABLE professores ADD COLUMN siape VARCHAR(20)"
            )
            connection.exec_driver_sql(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_professores_siape "
                "ON professores (siape)"
            )