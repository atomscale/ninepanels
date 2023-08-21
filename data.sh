clear
echo "\e[1;34mMANAGING DATA SCRIPT!!\e[0m"
echo

echo "Please select the environment you want to use:"

select env in "MAIN" "FEATURE"; do
    case $env in
    "MAIN")
        # source sh/set_env.sh MAIN localhost postgres 5434
        echo "You selected \033[1;34m$NINEPANELS_ENV\033[0m environment."
        select func in "SEE SCHEMA" "SEE DATA" "AMEND DATA"; do
            case $func in
            "SEE SCHEMA")
                cd src
                python -c "from data_mgmt import see_schema; see_schema()"
                cd ..
                break
                ;;
            "SEE DATA")
                cd src
                python -c "from data_mgmt import see_data; see_data()"
                cd ..
                break
                ;;
            "AMEND DATA")
                echo "yo, you kidding? this is prod!?!"
                break
                ;;
            *)
                echo "invalid slection"
                ;;
            esac
        done
        break
        ;;
    "FEATURE")
        echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment."
        source set_env.sh
        select func in "SEE SCHEMA" "SEE DATA" "SET UP DATA" "CLEAR DB"; do
            case $func in
            "SEE SCHEMA")

                python -m ninepanels.data_mgmt --read schema

                break
                ;;
            "SEE DATA")

                python -m ninepanels.data_mgmt --read data

                break
                ;;
            "SET UP DATA")

                python -m ninepanels.data_mgmt --create data

                break
                ;;
            "CLEAR DB")

                break
                ;;
            *)
                echo "invalid slection"
                ;;
            esac
        done
        break
        ;;
    *)
        echo "Invalid selection."
        ;;
    esac
done
