from datetime import datetime, timezone, timedelta
from pprint import PrettyPrinter


pp = PrettyPrinter()

panels = [
    {
        "id": 1,
        "position": 0,
        "title": "A",
        "created_at": datetime(2023, 8, 1, 13),
        "entries": [
            {
                "id": 5,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 1, 18, 3),
                "panel_id": 1,
            },
            {
                "id": 7,
                "is_complete": False,
                "timestamp": datetime(2023, 8, 1, 18),
                "panel_id": 1,
            },
            {
                "id": 8,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 1, 14),
                "panel_id": 1,
            },
            {
                "id": 11,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 4, 22),
                "panel_id": 1,
            },
            {
                "id": 14,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 10, 13),
                "panel_id": 1,
            },
            {
                "id": 98,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 11, 13),
                "panel_id": 1,
            },
            {
                "id": 99,
                "is_complete": False,
                "timestamp": datetime(2023, 8, 11, 13, 0, 1),
                "panel_id": 1,
            },
            {
                "id": 1987,
                "is_complete": True,
                "timestamp": datetime.utcnow(),
                "panel_id": 1,
            },

        ],
    },
    {
        "id": 2,
        "position": 1,
        "title": "B",
        "created_at": datetime(2023, 8, 20, 13),
        "entries": [
            {
                "id": 5,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 20, 18, 3),
                "panel_id": 2,
            },
            {
                "id": 6,
                "is_complete": False,
                "timestamp": datetime(2023, 8, 20, 18, 3, 25),
                "panel_id": 2,
            },
            {
                "id": 7,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 20, 18, 3, 25, 400),
                "panel_id": 2,
            },
            {
                "id": 8,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 21, 14),
                "panel_id": 2,
            },
            {
                "id": 11,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 22, 22),
                "panel_id": 2,
            },
            {
                "id": 14,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 24, 13),
                "panel_id": 2,
            },
            {
                "id": 98,
                "is_complete": True,
                "timestamp": datetime(2023, 8, 25, 13),
                "panel_id": 2,
            },
            {
                "id": 99,
                "is_complete": False,
                "timestamp": datetime(2023, 8, 25, 14, 1),
                "panel_id": 2,
            },
            {
                "id": 1987,
                "is_complete": True,
                "timestamp": datetime.utcnow() + timedelta(hours=-1),
                "panel_id": 2,
            },
            {
                "id": 1987,
                "is_complete": False,
                "timestamp": datetime.utcnow(),
                "panel_id": 2,
            },

        ],
    },
    {
        "id": 3,
        "position": 2,
        "title": "Created today",
        "created_at": datetime.utcnow() + timedelta(minutes=-2),
        "entries": [
            {
                "id": 534531,
                "is_complete": True,
                "timestamp": datetime.utcnow(),
                "panel_id": 3,
            },
        ],
    },
    {
        "id": 4,
        "position": 3,
        "title": "Created yesterday and completed yesterdy and today",
        "created_at": datetime.utcnow() + timedelta(days=-1),
        "entries": [
            {
                "id": 534531,
                "is_complete": True,
                "timestamp": datetime.utcnow() + timedelta(days=-1),
                "panel_id": 4,
            },
            {
                "id": 534531,
                "is_complete": True,
                "timestamp": datetime.utcnow(),
                "panel_id": 4,
            },
        ],
    }
]

# pp.pprint(panels)


def today() -> datetime:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return today


def calc_panel_age(created_at: datetime) -> int:
    panel_age = today() - created_at
    return panel_age.days + 2


print()
for panel in panels:
    print(f"Panel '{panel['title']}':")

    panel_age = calc_panel_age(created_at=panel["created_at"])
    print(f"{panel_age=}")

    date_range = []
    start_date = panel["created_at"]
    start_date = start_date.replace(hour=23, minute=59, second=59, microsecond=100000)

    date_range = []
    date_range.append(start_date)

    day_counter = 0

    for i in range(panel_age):
        day_counter += 1
        new_date = start_date + timedelta(days=day_counter)
        date_range.append(new_date)

    # pp.pprint(date_range)

    complete_counter = 0
    for date in date_range:
        day_matches = []


        for entry in panel["entries"]:
            if date.day == entry["timestamp"].day:
                day_matches.append(entry)

        if day_matches:
            sorted_day_match = sorted(day_matches, key=lambda x: x['timestamp'], reverse=True)
            if sorted_day_match[0]['is_complete'] == True:
                complete_counter += 1

    if panel_age > 0:
        panel_consistency = complete_counter/panel_age
    else:
        panel_consistency = 0
    print(f"{complete_counter=}")
    print(f"consistency for panel '{panel['title']}': {panel_consistency}")
    print()


