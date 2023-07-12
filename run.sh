source setenv.sh

echo -n "running \e[;34mninepanels\e[0m in mode \e[1;31m$MODE\e[0m, continue? Y/N? "

read answer

if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "running ninepanels in mode $MODE"
    uvicorn ninepanels.main:api
else
    echo "exiting"
    clear
fi