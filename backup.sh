echo "\e[1;34mBackup...\e[0m"
echo

echo "In \033[1;32m$NINEPANELS_ENV\033[0m environment"

select backup_opt in "Full dump" "Data only" "Exit"; do
    case $backup_opt in
    "Full dump")
        echo "backing up $NINEPANELS_ENV database..."

        # establish a timestamp to id this process
        clone_ts=$(date +"%Y%m%d%H%M%S")

        pg_dump --no-owner --no-acl -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres -t alembic_version -t users -t panels -t entries -t blacklisted_access_tokens -t password_reset_tokens -t timing_stats -t timings -F c >"/Users/bd/Library/CloudStorage/GoogleDrive-ben@atomscale.co/My Drive/databases/ninepanels/${clone_ts}_${NINEPANELS_ENV}.dump"
        echo "Database backup complete for selected tables"
        break
        ;;
    "Data only")
        echo "backing up $NINEPANELS_ENV database..."

        # establish a timestamp to id this process
        clone_ts=$(date +"%Y%m%d%H%M%S")

        pg_dump --no-owner --no-acl --data-only -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres -t alembic_version -t users -t panels -t entries -t blacklisted_access_tokens -t password_reset_tokens -t timing_stats -t timings > "/Users/bd/Library/CloudStorage/GoogleDrive-ben@atomscale.co/My Drive/databases/ninepanels/${clone_ts}_${NINEPANELS_ENV}_data_only.sql"
        echo "Database backup complete for selected tables"
        break
        ;;
    "Exit")
        break
        ;;
    *)
        echo "invalid selection"
        ;;
    esac
done

