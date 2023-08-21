clear
echo "\e[1;34mALEMBIC MIGRATIONS\e[0m"
echo

echo "MIGRATION.. proceed with care!!!"
echo "Please select the environment you want to use:"

select env in "FEATURE" ; do
    case $env in
        "FEATURE")
            source set_env.sh
            echo "You selected \033[1;32m$NINEPANELS_ENV\033[0m environment."
            echo "What do you want to do:"

            select action in "STAMP" "CREATE MIGRATION" "UPGRADE MANUALLY"  ; do
                case $action in
                    "STAMP")
                        alembic stamp head
                        echo "Stamped head"
                        break
                        ;;
                    "CREATE MIGRATION")

                        echo "Creating a migration..."
                        echo "Enter the migration message:"
                        read msg
                        alembic revision --autogenerate -m $msg
                        echo
                        echo "\e[1;31mnow check the migration file!\e[0m"
                        break
                        ;;
                    "UPGRADE MANUALLY")

                        echo "applying migration... are you sure?"
                        while true; do
                            read -q "response?Do you want to continue (Y/N)? "
                            echo ""

                            case $response in
                                'y'|'Y')
                                    echo "Applying migration"
                                    alembic upgrade head
                                    break ;;
                                'n'|'N')
                                    echo "You chose NO, getting out of here!!"
                                    break ;;
                                *)
                                    echo "Please enter Y or N." ;;
                            esac
                        done
                        break
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