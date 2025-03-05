#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>

int main(void)
{
    pid_t pid;
    pid_t ppid;

    pid = getpid();
    ppid = getppid();

    printf("pid = %d\n"
           "ppid = %d\n", pid, ppid);
    
    return 0;
}