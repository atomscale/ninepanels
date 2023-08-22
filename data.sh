clear
echo "\e[1;34mDATABASE COMMAND CENTRE\e[0m"
echo

# this scropt sets env, the rest are called

# manage
# backup
# migrate
# clone


continue_script=true

echo "Select environment:"
select env in "MAIN" "STAGING" "FEATURE" "Exit"; do
    case $env in
        "MAIN")
            source set_env_main.sh
            echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment BE CAREFUL!!!"
            echo "Set env vars for \033[1;32m$NINEPANELS_ENV\033[0m and connection to supabase PRODUCTION db"
            echo

            break
            ;;
        "STAGING")
            source set_env_staging.sh
            echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment."
            echo "Set env vars for \033[1;32m$NINEPANELS_ENV\033[0m and connection to supabase staging db"
            echo

            break
            ;;
        "FEATURE")
            source set_env_feature.sh
            echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment."
            echo "Set env vars for \033[1;32m$NINEPANELS_ENV\033[0m and connection to local postgres db"
            echo

            break
            ;;
        "Exit")
            echo "Finishing..."
            continue_script=false
            clear
            break
            ;;
        *)
            echo "invalid, try again"
            ;;
    esac
done

if $continue_script; then
    echo "Select action area:"
    select opt in "Manage schema/data" "Backup" "Restore" "Migrate" "Exit"; do
        case $opt in
            "Manage schema/data")
                source manage.sh
                break
                ;;
            "Backup")
                source backup.sh
                break
                ;;
            "Restore")
                source restore.sh
                break
                ;;
            "Migrate")
                source migrate.sh
                break
                ;;
            "Exit")
                echo "Finishing..."
                # continue_script=false
                break
                ;;
            *)
                echo "invalid, try again"
                ;;
        esac
    done
fi