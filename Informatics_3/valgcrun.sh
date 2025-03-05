gcc -o ./executors/$1.exe $1.c
valgrind ./executors/$1.exe 

