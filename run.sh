source set_env_feature.sh

clear
echo "\e[1;34mRUNNING SERVER LOCALLY\e[0m"
echo

uvicorn ninepanels.main:api 
