
echo "\e[1;34mRestore...\e[0m"
echo

echo "this restore will affect the $NINEPANELS_ENV database, replacing data there. Continue?"
select restore_opt in "Yes" "No"; do
    case $restore_opt in
        "Yes")
            echo "supply path to dump file"
            read dump_file_path

            echo "restoring $NINEPANELS_ENV database from $dump_file_path"

            # establish a timestamp to id this process
            clone_ts=$(date +"%Y%m%d%H%M%S")

            echo "Taking pre-restore backup..."
            pg_dump --no-owner --no-acl -U postgres -h $DB_HOSTNAME -p $DB_PORT -d postgres -t alembic_version -t users -t panels -t entries -F c >"/Users/bd/Library/CloudStorage/GoogleDrive-ben@atomscale.co/My Drive/databases/ninepanels/${clone_ts}_${NINEPANELS_ENV}.dump"

            echo "Pre-restore backup of target complete."
            echo


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
        "No")
            break
            ;;
    esac
done



