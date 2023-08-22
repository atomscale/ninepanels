
echo "\e[1;34mManage data and schema...\e[0m"
echo


keep_looping=true
while $keep_looping; do
    echo "Select database action:"
    select func in "CREATE SCHEMA" "CREATE DATA" "READ SCHEMA" "READ DATA" "CLEAR DB" "EXIT"; do
        case $func in
        "CREATE SCHEMA")

            if [ "$NINEPANELS_ENV" = "MAIN" ]; then
                echo "no chance mate, you're on main!"
                break
            fi
            python -m ninepanels.data_mgmt --create schema
            echo

            break
            ;;
        "CREATE DATA")

            if [ "$NINEPANELS_ENV" = "MAIN" ]; then
                echo "no chance mate, you're on main!"
                break
            fi
            python -m ninepanels.data_mgmt --create data
            echo

            break
            ;;
        "READ SCHEMA")

            python -m ninepanels.data_mgmt --read schema
            echo

            break
            ;;
        "READ DATA")

            python -m ninepanels.data_mgmt --read data
            echo

            break
            ;;
        "CLEAR DB")

            if [ "$NINEPANELS_ENV" = "MAIN" ]; then
                echo "no chance mate, you're on main!"
                break
            fi
            echo "Are you SURE you want to drop all??"
            select delete_action in "Yes, let's go" "Fucking no way"; do
                case $delete_action in
                    "Yes, let's go")
                        python -m ninepanels.data_mgmt --delete schema
                        break
                        ;;
                    "Fucking no way")
                        break
                        ;;
                esac
            done
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

