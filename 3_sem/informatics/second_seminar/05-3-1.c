#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main()
{
   int     fd[2], result;

   size_t size;
   char  resstring[14];
   char * name = "/bin/ls";
   char res_name[strlen(name) + 1];

   if(pipe(fd) < 0){
     printf("Can\'t open pipe\n");
     exit(-1);
   }

   result = fork();

   if(result < 0) {
      printf("Can\'t fork child\n");
      exit(-1);
   } else if (result > 0) {

     /* Parent process */

      close(fd[0]);

      size = write(fd[1], name, strlen(name) + 1);

      if(size != strlen(name) + 1){
        printf("Can\'t write all string to pipe\n");
        exit(-1);
      }

      close(fd[1]);
      printf("Parent exit\n");

   } else {

    /* Child process */

    close(fd[1]);

    if((read(fd[0], res_name, strlen(name) + 1)) != strlen(name) + 1)
    {
        perror("read");
        exit(EXIT_FAILURE);
    }

    execlp(res_name, res_name, 0);

    perror("execlp");
    
    exit(EXIT_FAILURE);

   }

   return 0;
}