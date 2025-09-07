#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>

int main() {
    pid_t pid, ppid;
    int a = 0;
    
    pid_t fork_result = fork();
    
    if (fork_result == 0) {
        a = a + 1;
        pid = getpid();
        ppid = getppid();
        printf("Child process: my pid = %d, my ppid = %d, result = %d\n", (int)pid, (int)ppid, a);
    } else if (fork_result > 0) {
        a = a + 10;
        pid = getpid();
        ppid = getppid();
        printf("Parent process: my pid = %d, my ppid = %d, result = %d\n", (int)pid, (int)ppid, a);
    } else {
        printf("Fork failed!\n");
    }
    
    return 0;
}
