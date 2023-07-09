from .database import engine
from . import sqlmodels as sql

from datetime import datetime
from sqlalchemy.orm import sessionmaker

sql.Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

ben = sql.User(name='BennyBOY')
hobo = sql.User(name="Hopythonboooobooooo")
christy = sql.User(name="Christoph")
db.add_all([ben, hobo, christy])
db.commit()

print("### USERS ###")
users = (
    db.query(sql.User)
    .all()
)
for user in users:
    print(user.id, user.name)

print()

new_panels = [
    sql.Panel(title="workout", owner_id=1),
    sql.Panel(title="write code", owner_id=1),
    sql.Panel(title="walk harris", owner_id=1),
    sql.Panel(title="cure cancer", owner_id=2),
    sql.Panel(title="move to oz", owner_id=3),
    sql.Panel(title="make pickles", owner_id=3),
    sql.Panel(title="move house again", owner_id=2),
]

db.add_all(new_panels)
db.commit()

print("### all panels ###")
panels = (
    db.query(sql.Panel)
    .all()
)

for panel in panels:
    print(panel.id, panel.title, panel.owner.name)

print()

user_id = 1

print(f"### ALL PANELS FOR USER {user_id} - method 1")
users_panels = (
    db.query(sql.Panel)
    .join(sql.User)
    .where(sql.User.id == user_id)
    .all()
)

for users_panel in users_panels:
    print(users_panel.title)

print()

# this method of directly going to the panel object only works if the user attr
# needed is available on the panel object.

# print(f"### ALL PANELS FOR USER {user_id} - method 2")
# users_panels = (
#     db.query(sql.Panel)
#     .where(sql.Panel.owner_id == user_id)
#     .all()
# )

# for users_panel in users_panels:
#     print(users_panel.title)

# print()

user_for_new_panel = db.query(sql.User).where(sql.User.id == 2).first()
new_panel = sql.Panel(title="anotoher thing")

print(user_for_new_panel.name)
try:
    user_for_new_panel.add_panel(new_panel)
    db.commit()
except ValueError as e:
    print(str(e))
    db.rollback()

print(f"### CHECK ALL PANELS FOR USER {user_id} ")
users_panels = (
    db.query(sql.Panel)
    .join(sql.User)
    .where(sql.User.id == user_id)
    .all()
)

for users_panel in users_panels:
    print(users_panel.title)

print()

print("### all panels ###")
panels = (
    db.query(sql.Panel)
    .all()
)

for panel in panels:
    print(panel.id, panel.title, panel.owner.name)

print()


ts = datetime.utcnow()

entries = [
    sql.Entry(is_complete=True, panel_id=1, timestamp=ts),
    sql.Entry(is_complete=False, panel_id=2),
    sql.Entry(is_complete=True, panel_id=3),
]
db.add_all(entries)
db.commit()

import time
time.sleep(1)

new_entry = sql.Entry(is_complete=False, panel_id=1, timestamp=datetime.utcnow())
db.add(new_entry)
db.commit()


panels_w_status = (
    db.query(sql.Entry)
    .join(sql.Panel)
    .join(sql.User)
    .where(sql.User.id == 1)
    .where(sql.Entry.is_complete == True)
    .all()
)

for pws in panels_w_status:
    print(pws.is_complete, pws.timestamp, pws.panel.title)

print()

benny_panels = (
    db.query(sql.Panel)
    .join(sql.User)
    .where(sql.User.id == 1)
    .all()
)

latest_panel_status = []

for panel in benny_panels:
    latest = (
        db.query(sql.Entry)
        .where(sql.Entry.panel_id == panel.id)
        .order_by(sql.Entry.timestamp.desc())
        .first()
    )

    if latest:
        latest_panel_status.append(latest)

for lps in latest_panel_status:
    print(lps.panel.title, lps.is_complete)