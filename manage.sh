
echo "\e[1;34mManage data and schema...\e[0m"
echo
echo "In \033[1;32m$NINEPANELS_ENV\033[0m environment"
echo


keep_looping=true
while $keep_looping; do
    echo "Select database action in \033[1;32m$NINEPANELS_ENV\033[0m:"
    select func in "Create schema" "Create data" "Read schema" "Read data" "Clear DB" "Exit"; do
        case $func in
        "Create schema")

            if [ "$NINEPANELS_ENV" = "MAIN" ]; then
                echo "no chance mate, you're on main!"
                break
            fi
            python -m ninepanels.data_mgmt --create schema
            echo

            break
            ;;
        "Create data")

            if [ "$NINEPANELS_ENV" = "MAIN" ]; then
                echo "no chance mate, you're on main!"
                break
            fi
            python -m ninepanels.data_mgmt --create data
            echo

            break
            ;;
        "Read schema")

            python -m ninepanels.data_mgmt --read schema
            echo

            break
            ;;
        "Read data")

            python -m ninepanels.data_mgmt --read data
            echo

            break
            ;;
        "Clear DB")

            if [ "$NINEPANELS_ENV" = "MAIN" ]; then
                echo "no chance mate, you're on main!"
                break
            fi
            echo "Are you SURE you want to drop all?? You are in \033[1;32m$NINEPANELS_ENV\033[0m environment"
            select delete_action in "Yes, let's go" "Nope, bail!"; do
                case $delete_action in
                    "Yes, let's go")
                        python -m ninepanels.data_mgmt --delete schema
                        break
                        ;;
                    "Nope, bail!")
                        break
                        ;;
                esac
            done
            break
            ;;
        "Exit")
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

