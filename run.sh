source setenv.sh

echo -n "running \e[;34mninepanels\e[0m in mode \e[1;31m$NINEPANELS_ENV\e[0m, continue? Y/N? "

read answer

if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "running ninepanels in mode $NINEPANELS_ENV"
    uvicorn ninepanels.main:api
else
    echo "exiting"
    clear
fi