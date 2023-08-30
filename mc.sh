clear
echo "\e[1;34mMISSION CONTROL\e[0m"
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
            echo "\033[1;31mYou selected\033[0m \033[1;32m$NINEPANELS_ENV\033[0m \033[1;31menvironment BE CAREFUL!!!\033[0m"
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
    select opt in "Manage schema/data" "Backup db" "Restore db" "Migrate db" "Ping server" "Exit"; do
        case $opt in
            "Manage schema/data")
                source manage.sh
                break
                ;;
            "Backup db")
                source backup.sh
                break
                ;;
            "Restore db")
                source restore.sh
                break
                ;;
            "Migrate db")
                source migrate.sh
                break
                ;;
            "Ping server")
                python -m ninepanels.ping
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