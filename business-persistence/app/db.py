import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    user = os.environ.get("DB_USER", "diyu_app")
    password = os.environ.get("DB_PASSWORD", "diyu_app_local_dev_only")
    host = os.environ.get("DB_HOST", "docker-db_postgres-1")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "diyu_business")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


engine = create_engine(database_url(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
