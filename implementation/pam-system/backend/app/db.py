import os
import time
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    base_dir = os.path.dirname(__file__)
    migration_path = os.path.join(base_dir, "..", "migrations", "001_init.sql")
    with open(migration_path, "r", encoding="utf-8") as handle:
        sql = handle.read()
    statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
    wait_for_db()
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def wait_for_db(retries: int = 20, delay: float = 1.5) -> None:
    for _ in range(retries):
        try:
            with engine.connect():
                return
        except Exception:
            time.sleep(delay)
    raise RuntimeError("Database not ready after retries")
