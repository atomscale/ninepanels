source set_env_test.sh

clear
echo "\e[1;34mRUNNING TESTS\e[0m"
echo

arg1=$1

if [[ $1 == "crud" ]]; then
    echo "crud..."
    pytest -v tests/test_crud.py
    return 0

elif [[ $1 == "api" ]]; then
    echo "crud..."
    pytest -v tests/test_api.py
    return 0

elif [[ $1 == "all" ]]; then
    echo "crud..."
    pytest -v
    return 0

else
    echo "define scope of tests: crud, api, all"
    return 0
fi
