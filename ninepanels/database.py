from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from . import config

import logging
from datetime import datetime
from dataclasses import dataclass
from collections import deque
import rollbar



engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_timeout=30
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@dataclass
class DBPerformanceMonitor:

    """Calculate db average call times and log out of nominal to logs and rollbar.

    Uses config settings

    perf_reading: microseconds

    """

    avg: int = 0
    readings = deque([], maxlen=config.DB_CALL_AVG_WINDOW)

    def monitor(self):
        if len(self.readings) == config.DB_CALL_AVG_WINDOW:
            self.avg = sum(self.readings) / len(self.readings)

    def report(self):
        logging.info(f"avg db call: {self.avg}ms")
        if self.avg > config.DB_PERF_ALERT_THRESHOLD:
            logging.warn(f"avg db call: {self.avg}ms over threshold {config.DB_PERF_ALERT_THRESHOLD}ms")
            rollbar.report_message(f"api: avg db call: {self.avg}ms over threshold {config.DB_PERF_ALERT_THRESHOLD}ms", level="warning")

    def add_reading(
        self, perf_reading_start: datetime, perf_reading_end: datetime
    ) -> None:
        op_duration = perf_reading_end - perf_reading_start
        self.readings.append(op_duration.microseconds / 1000)
        self.monitor()
        self.report()


db_monitor = DBPerformanceMonitor()


def get_db():
    start = datetime.utcnow()
    db = SessionLocal()
    try:
        yield db
    finally:
        end = datetime.utcnow()
        db_monitor.add_reading(start, end)
        db.close()
