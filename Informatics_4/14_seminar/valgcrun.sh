g++ -o ./executors/$1.exe $1.cpp
valgrind --leak-check=full ./executors/$1.exe 

