from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from nmap_service.config.app import cfg


def create_db_engine() -> Engine:
    settings = cfg()
    return create_engine(
        settings.db.database_url,
        echo=settings.db.echo_sql,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
        pool_timeout=settings.db.pool_timeout,
        pool_pre_ping=True,
    )


engine = create_db_engine()


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_ctx() -> Generator[Session, None, None]:
    """Context manager per uso al di fuori di FastAPI."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
