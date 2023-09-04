
echo "\e[1;34mRestore...\e[0m"
echo

echo "this restore will affect the \033[1;32m$NINEPANELS_ENV\033[0m database, replacing data there. Continue?"
select restore_opt in "Yes" "No"; do
    case $restore_opt in
        "Yes")
            select restore_type in "Full" "Data only"; do
                case $restore_type in
                    "Full")
                        echo "supply path to dump file"
                        read dump_file_path

                        echo "restoring $NINEPANELS_ENV database from $dump_file_path"

                        # establish a timestamp to id this process
                        clone_ts=$(date +"%Y%m%d%H%M%S")

                        echo "Taking pre-restore backup..."
                        pg_dump --no-owner --no-acl -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres -t alembic_version -t users -t panels -t entries -t blacklisted_access_tokens -t password_reset_tokens -F c >"/Users/bd/Library/CloudStorage/GoogleDrive-ben@atomscale.co/My Drive/databases/ninepanels/${clone_ts}_${NINEPANELS_ENV}.dump"

                        echo "Pre-restore full dump backup of restore target complete... moving to data only..."
                        echo

                        pg_dump --no-owner --no-acl --data-only -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres -t alembic_version -t users -t panels -t entries -t blacklisted_access_tokens  -t password_reset_tokens > "/Users/bd/Library/CloudStorage/GoogleDrive-ben@atomscale.co/My Drive/databases/ninepanels/${clone_ts}_${NINEPANELS_ENV}_data_only.sql"
                        echo "Pre-restore data-only dump backup of restore target complete."
                        echo

                        echo "Pre-restore backups of restore target complete."

                        echo "Dropping target database..."
                        dropdb --if-exists -U postgres -h $DB_HOSTNAME -p $DB_PORT postgres
                        if [ $? -ne 0 ]; then
                            echo "error occurred dropping db..."
                            return
                        fi
                        echo "Target database dropped."
                        echo

                        echo "Recreating target database..."
                        createdb -U postgres -h $DB_HOSTNAME -p $DB_PORT postgres
                        echo "Target database recreated"
                        echo

                        echo "Restoring data from the source file..."
                        pg_restore --no-owner -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres "$dump_file_path"
                        echo "Target database restored from source dump."


                        break
                        ;;
                    "Data only")
                        echo "\033[1;31mIs the schema in place but with no data??\033[0m"
                        echo "supply path to dump file:"
                        read dump_file_path

                        echo "restoring $NINEPANELS_ENV database from $dump_file_path"

                        # establish a timestamp to id this process
                        clone_ts=$(date +"%Y%m%d%H%M%S")

                        echo "Taking pre-restore backup..."
                        pg_dump --no-owner --no-acl -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres -t alembic_version -t users -t panels -t entries -t blacklisted_access_tokens -t password_reset_tokens -F c >"/Users/bd/Library/CloudStorage/GoogleDrive-ben@atomscale.co/My Drive/databases/ninepanels/${clone_ts}_${NINEPANELS_ENV}.dump"

                        echo "Pre-restore full dump backup of restore target complete... moving to data only..."
                        echo

                        pg_dump --no-owner --no-acl --data-only -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres -t alembic_version -t users -t panels -t entries -t blacklisted_access_tokens -t password_reset_tokens > "/Users/bd/Library/CloudStorage/GoogleDrive-ben@atomscale.co/My Drive/databases/ninepanels/${clone_ts}_${NINEPANELS_ENV}_data_only.sql"
                        echo "Pre-restore data-only dump backup of restore target complete."
                        echo

                        echo "Pre-restore backups of restore target complete."

                        echo "Restoring data from the source file..."
                        psql -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres < "$dump_file_path"
                        echo "Target database restored from source dump."
                        break
                        ;;
                    esac
                done
            break
            ;;
        "No")
            break
            ;;
    esac
done




