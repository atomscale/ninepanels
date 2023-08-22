""" this func is called by main to ensure the databses are int he correct state for testing.

not in vcs as this file kind of acts like api calls
can change across branches and not have to merge or affect core branch code

# DO NOT RUN THIS MANNUALLY use >> source data_mgmt.py instead and follow prompts

"""

from . import sqlmodels as sql
from . import config
from sqlalchemy import desc
from sqlalchemy import inspect
from .database import SessionLocal
from .database import engine, text

import argparse

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
    users = db.query(sql.User).all()
    for user in users:
        print(f"{user.id=} {user.name=}")


def create_schema():
    sql.Base.metadata.create_all(bind=engine)


def create_data():
    sql.Base.metadata.create_all(bind=engine)

    ben = sql.User(
        name="Ben",
        email="ben@ben.com",
        hashed_password="$2b$12$.leB8lTAJCrzGVMS/OLnYezTgwefS643AKI7Y2iZ9maxqkMPnx762",
    )

    db.add(ben)
    db.commit()

def update_date():
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

    if args.delete:
        if args.delete == "schema":
            delete_schema()


if __name__ == "__main__":
    main()
