#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, const char * argv[])
{   
    const char * name = "./my_fifo.fifo";

    if (argc > 1 && strcmp(argv[1], "-rm") == 0)
    {
        if(unlink(name) < 0)
        {
            printf("Can\'t remove FIFO\n");
            exit(-1);
        }

        exit(0);
    }

    umask(0);

    if((argc > 1) || mknod(name, S_IFIFO | 0666, 0) < 0){
        printf("Can\'t create FIFO\n");
        exit(-1);
    }
}