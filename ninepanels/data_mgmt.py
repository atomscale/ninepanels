""" this func is called by main to ensure the databses are int he correct state for testing.

not in vcs as this file kind of acts like api calls
can change across branches and not have to merge or affect core branch code

# DO NOT RUN THIS MANNUALLY use >> source data_mgmt.py instead and follow prompts

"""

from . import sqlmodels as sql
from sqlalchemy import desc
from sqlalchemy import inspect
from .database import SessionLocal
from .database import engine

import argparse



sql.Base.metadata.create_all(bind=engine)
db = SessionLocal()

def see_schema():

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

def see_data() -> None:


    users = db.query(sql.User).all()
    for user in users:
        print(f"{user.id=} {user.first_name=}")


def set_up_data():

    print(f"no data created yet need to set up a core place for this to be used locally runnign and across tests")

def amend_data():
    pass

def drop_tables():
    sql.Base.metadata.drop_all(bind=engine)
    print(f"dropped tables")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--read', type=str, help="see the schema of the db")
    parser.add_argument('--create', type=str, help="see the schema of the db")

    args = parser.parse_args()

    print(args.read)

    if args.read:
        if args.read == "schema":
            see_schema()
        elif args.read == "data":
            see_data()
        else:
            pass

    if args.create:
        if args.create == "data":
            set_up_data()

if __name__ == "__main__":
    main()