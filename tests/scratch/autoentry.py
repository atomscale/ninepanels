import random
from datetime import timedelta, datetime

from pprint import PrettyPrinter

pp = PrettyPrinter()

def generate_panel_history() -> list:

    # generate a list of timestamps from today to rand len max 250

    # for each date randomly select true false

    panel_len = random.randint(8,250)
    today = datetime.utcnow()

    entries = []
    for d in range(panel_len):
        delta = timedelta(days=-d)
        panel_entry = {
            "is_complete": random.choice([True, False]),
            "timestamp": today + delta
        }
        entries.append(panel_entry)

    return entries

entries = generate_panel_history()
pp.pprint(entries)