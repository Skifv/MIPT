#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
   int     fd[2];
   char    string[] = "Hello, world!";
   char    resstring[14];

   if(pipe(fd) < 0){
     printf("Can\'t open pipe\n");
     exit(-1);
   }

   if(write(f d[1], string, 14) != 14){
     printf("Can\'t write all string to pipe\n");
     exit(-1);
   }

   if(read(fd[0], resstring, 14) < 0){
      printf("Can\'t read string from pipe\n");
      exit(-1);
   }

   printf("%s\n", resstring);

   close(fd[0]);
   close(fd[1]);

   return 0;
}