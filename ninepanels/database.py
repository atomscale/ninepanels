from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import text # keep, imported eslewhere
from sqlalchemy.orm import sessionmaker
import rollbar

from . import config


engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_timeout=30
)

in_alert = False

def see_status_checkout(dbapi_con, con_record, con_proxy):
    global in_alert
    msg = engine.pool.status()
    num_connections = int(msg[-1])
    alert_threshold = 6
    if num_connections > alert_threshold:
        if not in_alert:
            in_alert = True
            rollbar.report_message(message=f"db connection pool > {alert_threshold}", level='warn')
    else:
        in_alert = False

def see_status_checkin(dbapi_con, con_record):
    global in_alert
    msg = engine.pool.status()
    num_connections = int(msg[-1])
    alert_threshold = 6
    if num_connections > alert_threshold:
        if not in_alert:
            in_alert = True
            rollbar.report_message(message=f"db connection pool > {alert_threshold}", level='warn')
    else:
        in_alert = False

event.listen(engine.pool, 'checkout', see_status_checkout)
event.listen(engine.pool, 'checkin', see_status_checkin)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
