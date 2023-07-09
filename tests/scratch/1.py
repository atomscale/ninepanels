from datetime import datetime, timedelta

first = datetime.utcnow()
diff = timedelta(seconds=1)
print(first)
print(first + diff)