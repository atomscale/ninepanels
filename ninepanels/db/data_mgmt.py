""" this func is called by main to ensure the databases are int he correct state for testing.

not in vcs as this file kind of acts like api calls
can change across branches and not have to merge or affect core branch code

# DO NOT RUN THIS MANNUALLY use >> source data_mgmt.py instead and follow prompts

"""

import argparse
from datetime import datetime, timedelta

from sqlalchemy import desc
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from .. import sqlmodels as sql
from ..core import config


def read_schema(engine):
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


def read_data(db) -> None:
    print("USERS:")
    print()
    users = db.query(sql.User).all()
    if users:
        for user in users:
            print(f"{user.id=} {user.name=}: {user.is_admin}")
            print()
            # if user.panels:
            #     for i, panel in enumerate(user.panels):
            #         print(f"{panel.id=}, {panel.created_at}, {panel.position=}")
            #     print()
            # print()


def create_schema(engine):
    sql.Base.metadata.create_all(bind=engine)


def create_data(engine, db: Session):
    sql.Base.metadata.create_all(bind=engine)

    entries_a = [
        # {
        #     "is_complete": True,
        #     "timestamp": datetime(2023, 8, 1, 18, 3),
        # },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 2, 14),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 4, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 11, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 13, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 15, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 16, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 17, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 19, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 20, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 26, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 27, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 22, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 29, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 31, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 6, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 11, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 13, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 14, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 19, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 20, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 26, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 27, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 28, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 29, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 30, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 10, 1, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 10, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 10, 4, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 10, 5, 13),
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
            "timestamp": datetime(2023, 8, 27, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 29, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 31, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 3, 13),
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
            "timestamp": datetime(2023, 8, 3, 23),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 5, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 6, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 8, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 9, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 29, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 31, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 3, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime.utcnow(),
        },
    ]

    entries_d = [
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 4, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 5, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 6, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 8, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 9, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 11, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 13, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 15, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 17, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 19, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 20, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 27, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 22, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 29, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 31, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 3, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime.utcnow(),
        },
    ]

    entries_e = [
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 4, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 5, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 6, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 8, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 9, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 11, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 13, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 31, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 3, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime.utcnow(),
        },
    ]

    entries_f = [
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 4, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 5, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 6, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 8, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 9, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 11, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 13, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 15, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 17, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 19, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 20, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 27, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 22, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 29, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 31, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 3, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime.utcnow(),
        },
    ]

    entries_g = [
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 4, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 5, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 6, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime.utcnow(),
        },
    ]

    entries_h = [
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 4, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 5, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 6, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 8, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 9, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 11, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 13, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 15, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 17, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 19, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 20, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 27, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 22, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 29, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 31, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 3, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime.utcnow(),
        },
    ]

    entries_i = [
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 4, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 5, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 6, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 8, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 9, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 11, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 13, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 15, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 17, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 19, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 20, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 27, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 22, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 29, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 8, 31, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 3, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 28, 22),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 29, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 9, 30, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 10, 1, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 10, 2, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime(2023, 10, 4, 13),
        },
        {
            "is_complete": True,
            "timestamp": datetime.utcnow(),
        },
    ]

    sql_entries_a = [sql.Entry(**entry) for entry in entries_a]
    sql_entries_b = [sql.Entry(**entry) for entry in entries_b]
    sql_entries_c = [sql.Entry(**entry) for entry in entries_c]
    sql_entries_d = [sql.Entry(**entry) for entry in entries_d]
    sql_entries_e = [sql.Entry(**entry) for entry in entries_e]
    sql_entries_f = [sql.Entry(**entry) for entry in entries_f]
    sql_entries_g = [sql.Entry(**entry) for entry in entries_g]
    sql_entries_h = [sql.Entry(**entry) for entry in entries_h]
    sql_entries_i = [sql.Entry(**entry) for entry in entries_i]

    new_panels = [
        sql.Panel(
            position=0,
            title="The test panel",
            description="This is the recent and testing panel! 💪😎 With a very loong description. This is the recent and testing panel! 💪😎 With a very loong description. This is the recent and testing panel! 💪😎 With a very loong description. This is the recent and testing panel! 💪😎 With a very loong description. This is the recent and testing panel! 💪😎 With a very loong description. This is the recent and testing panel! 💪😎 With a very loong description. This is the recent and testing panel! 💪😎 With a very loong description. This is the recent and testing panel! 💪😎 With a very loong description",
            entries=sql_entries_a,
            created_at=datetime(2023, 8, 1, 13),
        ),
        sql.Panel(
            position=1,
            title="Do 10 minutes of house cleaning/tidy",
            entries=sql_entries_b,
            created_at=datetime(2023, 8, 20, 13),
        ),
        sql.Panel(
            position=2,
            title="Find and email one contact with app link 🚀",
            description="See ya later...geddit?",
            entries=sql_entries_c,
            created_at=datetime(2023, 9, 2, 13),
        ),
        sql.Panel(
            position=3,
            title="Deep flow at work, connect with purpose of job",
            description="Donkey Kong",
            entries=sql_entries_d,
            created_at=datetime(2023, 8, 1, 13),
        ),
        sql.Panel(
            position=4,
            title="Read in bed before sleep",
            description="Donkey Kong",
            entries=sql_entries_e,
            created_at=datetime(2023, 8, 23, 13),
        ),
        sql.Panel(
            position=5,
            title="Cook from scratch, no snacks",
            description="Donkey Kong",
            entries=sql_entries_f,
            created_at=datetime(2023, 8, 1, 13),
        ),
        sql.Panel(
            position=6,
            title="Aerobic heavy breathing",
            description="Donkey Kong",
            entries=sql_entries_g,
            created_at=datetime(2023, 8, 18, 13),
        ),
        sql.Panel(
            position=7,
            title="Meditate",
            description="Donkey Kong",
            entries=sql_entries_h,
            created_at=datetime(2023, 8, 5, 13),
        ),
        sql.Panel(
            position=8,
            title="Focussed time with D, play games",
            description="Donkey Kong",
            entries=sql_entries_i,
            created_at=datetime(2023, 8, 5, 13),
        ),
    ]

    bwdyer = sql.User(
        name="bwdyer",
        email="bwdyer@gmail.com",
        is_admin=True,
        hashed_password="$2b$12$.leB8lTAJCrzGVMS/OLnYezTgwefS643AKI7Y2iZ9maxqkMPnx762",
        panels=new_panels,
    )

    db.add(bwdyer)
    db.commit()

    ben = sql.User(
        name="Ben",
        email="ben@atomscale.co",
        is_admin=False,
        hashed_password="$2b$12$.leB8lTAJCrzGVMS/OLnYezTgwefS643AKI7Y2iZ9maxqkMPnx762",
    )

    db.add(ben)
    db.commit()


def update_data(db: Session):
    users = db.query(sql.User).all()

    print("PRE UPDATE")
    for user in users:
        print(f"{user.email=}: {user.is_admin=}")

    try:
        for user in users:
            user.is_admin = False
        db.commit()
    except SQLAlchemyError as e:
        print(f"error in update {str(e)}")
        db.rollback()

    print("POST UPDATE")
    for user in users:
        print(f"{user.email=}: {user.is_admin=}")

    # me = db.query(sql.User).filter(sql.User.email == "bwdyer@gmail.com").first()

    # if me:
    #     try:
    #         me.is_admin = True
    #         db.commit()
    #     except SQLAlchemyError as e:
    #         print(f"error in update {str(e)}")
    #         db.rollback()

    #     print("udpated me to admin")
    #     print()
    # else:
    #     print("didnt find me ")


def delete_schema(engine, db, text):
    sql.Base.metadata.drop_all(bind=engine)
    db.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.commit()
    print(f"dropped tables")


def main():
    from .database import SessionLocal
    from .database import engine, text

    db = SessionLocal()

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
            create_schema(engine)
        if args.create == "data":
            create_data(engine=engine, db=db)

    if args.read:
        if args.read == "schema":
            read_schema(engine)
        elif args.read == "data":
            read_data(db)
        else:
            pass

    if args.apply:
        if args.apply == "update":
            update_data(db=db)

    if args.delete:
        if args.delete == "schema":
            delete_schema(engine, db, text=text)


if __name__ == "__main__":
    main()
