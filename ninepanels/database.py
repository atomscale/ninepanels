from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlite3 import Connection as SQLiteConnection

from .config import SQLALCHEMY_DATABASE_URI


if "sqlite" in SQLALCHEMY_DATABASE_URI:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_timeout=30
    )


@event.listens_for(engine, "connect")
def _set_fk_pragma(conn, conn_record):
    if isinstance(conn, SQLiteConnection):
        cur = conn.cursor()
        cur.execute("pragma foreign_keys=1;")
        cur.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()