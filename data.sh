clear
echo "\e[1;34mMANAGING DATA SCRIPT!!\e[0m"
echo


select env in "STAGING" "FEATURE"; do
    case $env in
        "STAGING")
            source set_env_staging.sh
            echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment."
            echo "Set satging env vars for satging and lconneciton to supabase staging db"

            break
            ;;
        "FEATURE")
            source set_env_feature.sh
            echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment."
            echo "Set local env vars for feature branch and local db connection"

            break
            ;;
        *)
            echo "invalid, try again"
            ;;
    esac
done
echo

keep_looping=true
while $keep_looping; do
    select func in "CREATE SCHEMA" "CREATE DATA" "READ SCHEMA" "READ DATA" "CLEAR DB" "EXIT"; do
        case $func in
        "CREATE SCHEMA")

            python -m ninepanels.data_mgmt --create schema

            break
            ;;
        "CREATE DATA")

            python -m ninepanels.data_mgmt --create data

            break
            ;;
        "READ SCHEMA")

            python -m ninepanels.data_mgmt --read schema

            break
            ;;
        "READ DATA")

            python -m ninepanels.data_mgmt --read data

            break
            ;;
        "CLEAR DB")

            if [ "$NINEPANELS_ENV" = "STAGING" ]; then
                echo "no chance mate"
                break
            fi

            echo "data would have been deleted"
            python -m ninepanels.data_mgmt --delete schema
            break
            ;;
        "EXIT")
            echo "finished.."
            keep_looping=false
            break
            ;;
        *)
            echo "invalid slection"
            ;;
        esac
    done
done

