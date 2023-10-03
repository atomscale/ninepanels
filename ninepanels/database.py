from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import text # keep, imported eslewhere
from sqlalchemy.orm import sessionmaker

from . import config


engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_timeout=30
)

# def see_status_checkout(dbapi_con, con_record, con_proxy):
#     print(engine.pool.status())

# def see_status_checkin(dbapi_con, con_record):
#     print(engine.pool.status())

# event.listen(engine.pool, 'checkout', see_status_checkout)
# event.listen(engine.pool, 'checkin', see_status_checkin)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
