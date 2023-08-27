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

    # print(f"panel query as per prod")
    # panels = db.query(sql.Panel).join(sql.User).where(sql.User.id == 1).all()
    # for panel in panels:
    #     print(f"{panel.id=}, {panel.title=}, {panel.position=}")

    # print(f"Panel query as per app - new:")
    # panels = crud.read_all_panels_by_user(db=db, user_id=4)

    # for panel in panels:
    #     print(f"{panel.id=}, {panel.title=}, {panel.position=}")


def create_schema():
    sql.Base.metadata.create_all(bind=engine)


def create_data():
    sql.Base.metadata.create_all(bind=engine)

    ben = sql.User(
        name="Ben",
        email="ben@ben.com",
        hashed_password="$2b$12$.leB8lTAJCrzGVMS/OLnYezTgwefS643AKI7Y2iZ9maxqkMPnx762",
    )

    bec = sql.User(
        name="Bec",
        email="bec@bec.com",
        hashed_password="$2b$12$.leB8lTAJCrzGVMS/OLnYezTgwefS643AKI7Y2iZ9maxqkMPnx762",
    )

    db.add(ben)
    db.add(bec)
    db.commit()

    panels = [
        sql.Panel(
            position=0,
            title="A",
            description="Long panel description detialing cool stuff",
            user_id=ben.id,
        ),
        sql.Panel(
            # position=1,
            title="B",
            description="Long panel description detialing cool stuff",
            user_id=ben.id,
        ),
        sql.Panel(
            # position=2,
            title="C",
            description="Long panel description detialing cool stuff",
            user_id=ben.id,
        ),
        sql.Panel(
            # position=0,
            title="A",
            description="Long panel description detialing cool stuff",
            user_id=bec.id,
        ),
        sql.Panel(
            # position=1,
            title="B",
            description="Long panel description detialing cool stuff",
            user_id=bec.id,
        ),
        sql.Panel(
            # position=2,
            title="C",
            description="Long panel description detialing cool stuff",
            user_id=bec.id,
        ),
    ]
    db.add_all(panels)
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
