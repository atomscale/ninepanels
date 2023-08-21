clear
echo "\e[1;34mBUILD STAGING\e[0m"
echo


# establish a timestamp to id this process
clone_ts=$(date +"%Y%m%d%H%M%S")

# take dump from source
pg_dump -U postgres -h localhost -p 5434 -d postgres -F c > "clones/${clone_ts}_maindev_dump.dump"
echo "source dump complete"

# take backup of target
pg_dump -U postgres -h localhost -p 5433 -d postgres -F c > "clones/${clone_ts}_localdev_preclone_dump.dump"
echo "target backup complete"

# drop target
dropdb --if-exists -U postgres -h localhost -p 5433 postgres
echo "Target database dropped"

# Create target
createdb -U postgres -h localhost -p 5433 postgres
echo "Target database recreated"

# Restore target from the source dump
pg_restore -U postgres -h localhost -p 5433 -d postgres "clones/${clone_ts}_maindev_dump.dump"
echo "Target database restored from source dump"