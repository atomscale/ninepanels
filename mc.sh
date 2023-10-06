clear
echo "\e[1;34mMISSION CONTROL\e[0m"
echo

# this scropt sets env, the rest are called

# manage
# backup
# migrate


continue_script=true

echo "Select environment:"
select env in "MAIN" "STAGING" "FEATURE" "TEST" "Exit"; do
    case $env in
        "MAIN")
            current_branch=$(git symbolic-ref --short HEAD)

            if [[ "$current_branch" != "main" ]]; then
                echo "you cannot select MAIN env while on branch $current_branch"
                return 1
            else
                source set_env_main.sh
                echo "\033[1;31mYou selected\033[0m \033[1;32m$NINEPANELS_ENV\033[0m \033[1;31menvironment BE CAREFUL!!!\033[0m"
                echo "Set env vars for \033[1;32m$NINEPANELS_ENV\033[0m and connection to supabase PRODUCTION db"
                echo
            fi

            break
            ;;
        "STAGING")
            current_branch=$(git symbolic-ref --short HEAD)

            if [[ "$current_branch" != "staging" ]]; then
                echo "you cannot select STAGING env while on branch $current_branch"
                return 1
            else
                source set_env_staging.sh
                echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment."
                echo "Set env vars for \033[1;32m$NINEPANELS_ENV\033[0m and connection to supabase staging db"
                echo
            fi

            break
            ;;
        "FEATURE")
            current_branch=$(git symbolic-ref --short HEAD)

            if [[ "$current_branch" == "staging" || "$current_branch" == "main" ]]; then
                echo "you cannot select FEATURE env while on branch $current_branch"
                return 1
            else
                echo "You are on branch: \e[1;34m$current_branch\e[0m"
                source set_env_feature.sh
                echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment, so that's okay."
                echo "Set env vars for \033[1;32m$NINEPANELS_ENV\033[0m and connection to local postgres db"
                echo
            fi

            break
            ;;
        "TEST")
            current_branch=$(git symbolic-ref --short HEAD)


            echo "You are on branch: \e[1;34m$current_branch\e[0m"
            source set_env_test.sh
            echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment, so that's okay."
            echo "Set env vars for \033[1;32m$NINEPANELS_ENV\033[0m and connection to local postgres db"
            echo


            break
            ;;
        "Exit")
            echo "Finishing..."
            return 1
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