#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>

#define CHILD 0
#define FAIL -1

int main(int argc, char *argv[], char *envp[]) {

    pid_t main_process = getpid();

    pid_t fork_result = fork();
    
    switch (fork_result)
    {
    case CHILD:
        printf("## Child process ##\n\n");
        execl("./argv_envp.exe", "./argv_envp.exe", 0);
        break;
    case FAIL:
        printf("Error on program start\n");
        exit(-1);
     default:
        printf("## Parent process ##\n\n");
        execl("./icat.exe", "./icat.exe", 0);
        break;
    }
    
    return 0;
}
