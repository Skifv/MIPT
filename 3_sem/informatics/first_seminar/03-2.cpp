#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <cstdlib>


int main(int argc, char *argv[], char *envp[])
{ 
execle("/bin/cat", "/bin/cat", "03-2.cpp", 0, envp);

printf("Error on program start\n");
exit(-1);
return 0; 
}