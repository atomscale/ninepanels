from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import config


engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_timeout=30
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
