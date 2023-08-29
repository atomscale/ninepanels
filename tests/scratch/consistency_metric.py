from datetime import datetime, timezone, timedelta
from pprint import PrettyPrinter
import pandas as pd

pp = PrettyPrinter()

panels = [
    {
        "id": 1,
        "position": 0,
        "title": "A",
        "created_at": "2023-08-01T23:59:59.1",
        "entries": [
            {
                "id": 7,
                "is_complete": True,
                "timestamp": "2023-08-01T18:00:00.0",
                "panel_id": 1,
            },
            {
                "id": 8,
                "is_complete": True,
                "timestamp": "2023-08-02T18:00:00.0",
                "panel_id": 1,
            },
            {
                "id": 11,
                "is_complete": False,
                "timestamp": "2023-08-02T19:00:00.0",
                "panel_id": 1,
            },
            {
                "id": 14,
                "is_complete": True,
                "timestamp": "2023-08-05T18:00:00.0",
                "panel_id": 1,
            },
            {
                "id": 98,
                "is_complete": True,
                "timestamp": "2023-08-09T18:00:00.0",
                "panel_id": 1,
            },
            {
                "id": 99,
                "is_complete": False,
                "timestamp": "2023-08-09T19:00:00.0",
                "panel_id": 1,
            },
        ],
    }
]

# pp.pprint(panels)

def today() -> datetime:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return today

def panel_age(created_at: datetime) -> int:
    panel_age = (today() - datetime.fromisoformat(created_at))
    return panel_age.days + 1

print()
for panel in panels:
    print(f"Panel {panel['title']}:")

    panel_age = panel_age(created_at=panel['created_at'])
    print(f"{panel_age=}")


    date_range = pd.date_range(datetime.fromisoformat(panel['created_at']), datetime.now(), freq="D")

    for date in date_range:
        print(date)

