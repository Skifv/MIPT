#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>

int main(int argc, char *argv[], char *envp[]) {
    pid_t fork_result = fork();
    
    if (fork_result == 0) {
        printf("Child process!\n\n");

        execle("./argv_envp.exe", "./argv_envp.exe", 0, envp);
    } else if (fork_result > 0) {
        printf("\n\n## I am parent ##\n\n");;
    } else {
        printf("Fork failed!\n");
    }
    
    return 0;
}
