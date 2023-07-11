from datetime import datetime, timedelta

now = datetime.utcnow()
day_now = now.replace(hour=0, minute=0, second=0, microsecond=1)
print(day_now)