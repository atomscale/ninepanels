
echo "\e[1;34mBackup...\e[0m"
echo

select backup_opt in "Yes" "No"; do
    case $backup_opt in
        "Yes")
            echo "backup up $NINEPANELS_ENV database"

            # establish a timestamp to id this process
            clone_ts=$(date +"%Y%m%d%H%M%S")

            pg_dump --no-owner --no-acl -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres -t alembic_version -t users -t panels -t entries -F c > "backups/${clone_ts}_${NINEPANELS_ENV}_dump.dump"
            echo "selected tables database backup complete"
            break
            ;;
    esac
done


# # take backup of target
# pg_dump -U postgres -h localhost -p 5433 -d postgres -F c > "clones/${clone_ts}_localdev_preclone_dump.dump"
# echo "target backup complete"

# # drop target
# dropdb --if-exists -U postgres -h localhost -p 5433 postgres
# echo "Target database dropped"

# # Create target
# createdb -U postgres -h localhost -p 5433 postgres
# echo "Target database recreated"

# # Restore target from the source dump
# pg_restore -U postgres -h localhost -p 5433 -d postgres "clones/${clone_ts}_maindev_dump.dump"
# echo "Target database restored from source dump"