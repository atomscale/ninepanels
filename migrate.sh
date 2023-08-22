
echo "\e[1;34mSchema migrations...\e[0m"
echo

echo "MIGRATION.. proceed with care!!!"
echo

select action in "Stamp" "Create Migration" "Upgrade Manually" ; do
    case $action in
        "Stamp")
            alembic stamp head
            echo "Stamped head"
            break
            ;;
        "Create Migration")

            echo "Creating a migration..."
            echo "Enter the migration message:"
            read msg
            alembic revision --autogenerate -m $msg
            echo
            echo "\e[1;31mnow check the migration file!\e[0m"
            break
            ;;
        "Upgrade Manually")

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
