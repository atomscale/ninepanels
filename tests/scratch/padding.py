from datetime import datetime, timedelta

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

now = datetime.utcnow()


arr = [
    {"dn": 0, "is_pad": False, "panel_date": datetime(day=26, month=2, year=2024)},
    {"dn": 6, "is_pad": False, "panel_date": datetime(day=25, month=2, year=2024)},
    {"dn": 5, "is_pad": False, "panel_date": datetime(day=24, month=2, year=2024)},
    {"dn": 4, "is_pad": False, "panel_date": datetime(day=23, month=2, year=2024)},
    {"dn": 3, "is_pad": False, "panel_date": datetime(day=22, month=2, year=2024)},
    {"dn": 2, "is_pad": False, "panel_date": datetime(day=21, month=2, year=2024)},
    {"dn": 1, "is_pad": False, "panel_date": datetime(day=20, month=2, year=2024)},
]


def pad_arr(arr: list):

    padded = [*arr]

    # pad start
    if arr[0]["dn"] != 6:
        days_to_pad = 6 - arr[0]["dn"]
        for i in range(0, days_to_pad):
            pad_date = arr[0]["panel_date"] + timedelta(days=days_to_pad - i)
            pad_day = {"dn": pad_date.weekday(), "is_pad": True, "panel_date": pad_date}
            padded.insert(i, pad_day)

    # pad end
    if arr[-1]["dn"] != 0:
        days_to_pad = arr[-1]["dn"]
        for i in range(days_to_pad):
            pad_date = arr[-1]["panel_date"] - timedelta(days=i + 1)
            pad_day = {"dn": pad_date.weekday(), "is_pad": True, "panel_date": pad_date}
            padded.append(pad_day)

    return padded


pp.pprint(pad_arr(arr))
