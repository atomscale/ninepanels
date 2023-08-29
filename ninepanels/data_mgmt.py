""" this func is called by main to ensure the databses are int he correct state for testing.

not in vcs as this file kind of acts like api calls
can change across branches and not have to merge or affect core branch code

# DO NOT RUN THIS MANNUALLY use >> source data_mgmt.py instead and follow prompts

"""

from . import sqlmodels as sql
from . import config
from . import crud
from sqlalchemy import desc
from sqlalchemy import inspect
from .database import SessionLocal
from .database import engine, text

import argparse
from datetime import datetime, timedelta

db = SessionLocal()


def read_schema():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"db tables:")
    print(f"    {tables}")
    print()

    for table in tables:
        print(f"cols for {table}:")
        columns = inspector.get_columns(table_name=table)
        for column in columns:
            print(f"   {column['name']}")


def read_data() -> None:
    print("USERS:")
    print()
    users = db.query(sql.User).all()
    for user in users:
        print(f"{user.id=} {user.name=}:")
        print()
        for i, panel in enumerate(user.panels):
            print(f"{panel.id=}: {panel.position=}: cur index = {i}")
            print()
        print()
    print()


def create_schema():
    sql.Base.metadata.create_all(bind=engine)


def create_data():
    sql.Base.metadata.create_all(bind=engine)

    entries_a = [
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 1, 18, 3),
        },
        {
            "is_complete": False,
            "timestamp": datetime(2023, 8, 1, 18),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 1, 14),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 4, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 10, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 11, 13),
        },
        {
            "is_complete": False,
            "timestamp": datetime(2023, 8, 11, 13, 0, 1),
        },
        {
            "is_complete": True,
            "timestamp": datetime.utcnow(),
        },
    ]

    entries_b = [
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 20, 18, 3),
        },
        {
            "is_complete": False,
            "timestamp": datetime(2023, 8, 20, 18, 3, 25),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 20, 18, 3, 25, 400),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 21, 14),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 22, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 24, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 25, 13),
        },
        {
            "is_complete": False,
            "timestamp": datetime(2023, 8, 25, 14, 1),
        },
        {
            "is_complete": True,
            "timestamp": datetime.utcnow() + timedelta(hours=-1),
        },
        {
            "is_complete": False,
            "timestamp": datetime.utcnow(),
        },
    ]

    entries_c = [
        {
            "is_complete": True,
            "timestamp": datetime.utcnow(),
        },
    ]

    entries_d = [
        {
            "is_complete": True,
            "timestamp": datetime.utcnow() + timedelta(days=-1),
        },
        {
            "is_complete": False,
            "timestamp": datetime.utcnow(),
        },
    ]

    sql_entries_a = [sql.Entry(**entry) for entry in entries_a]
    sql_entries_b = [sql.Entry(**entry) for entry in entries_b]
    sql_entries_c = [sql.Entry(**entry) for entry in entries_c]
    sql_entries_d = [sql.Entry(**entry) for entry in entries_d]

    new_panels = [
        sql.Panel(
            position=0,
            title="A",
            description="AAAAH this is cool",
            entries=sql_entries_a,
            created_at=datetime(2023, 8, 1, 13),
        ),
        sql.Panel(
            position=1,
            title="B",
            description="to make it look lvery  nice",
            entries=sql_entries_b,
            created_at=datetime(2023, 8, 20, 13),
        ),
        sql.Panel(
            position=2,
            title="Created today",
            description="See ya later...geddit?",
            entries=sql_entries_c,
            created_at=datetime.utcnow() + timedelta(minutes=-2),
        ),
        sql.Panel(
            position=3,
            title="Created yesterday completed today",
            description="Donkey Kong",
            entries=sql_entries_d,
            created_at=datetime.utcnow() + timedelta(days=-1),
        ),
    ]

    ben = sql.User(
        name="Ben",
        email="ben@ben.com",
        hashed_password="$2b$12$.leB8lTAJCrzGVMS/OLnYezTgwefS643AKI7Y2iZ9maxqkMPnx762",
        panels=new_panels,
    )

    db.add(ben)
    db.commit()


def update_data():
    pass


def delete_schema():
    sql.Base.metadata.drop_all(bind=engine)
    db.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.commit()
    print(f"dropped tables")


def main():
    print(
        f"data_mgmt.py operating on branch {config.branch} in env {config.CURRENT_ENV}"
    )
    print()
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", type=str)
    parser.add_argument("--read", type=str)
    parser.add_argument("--apply", type=str)
    parser.add_argument("--delete", type=str)

    args = parser.parse_args()

    if args.create:
        if args.create == "schema":
            create_schema()
        if args.create == "data":
            create_data()

    if args.read:
        if args.read == "schema":
            read_schema()
        elif args.read == "data":
            read_data()
        else:
            pass

    if args.apply:
        if args.apply == "update":
            update_data()

    if args.delete:
        if args.delete == "schema":
            delete_schema()


if __name__ == "__main__":
    main()
