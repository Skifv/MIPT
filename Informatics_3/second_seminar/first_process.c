#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
   int     fd;

   char string[20] = "Hello, Vladislav!!!";

   char    name[] = "./my_fifo.fifo";
   
   /* First process */

   if((fd = open(name, O_WRONLY)) < 0){
      perror("open");
      printf("Can\'t open FIFO for writting\n");
   exit(-1);
   }

   if(write(fd, string, sizeof(string)) != sizeof(string)){
      printf("Can\'t write all string to FIFO\n");
      exit(-1);
   }

   if(close(fd) < 0)
   {
      printf("Can\'t close FIFO to write\n");
      exit(-1);
   }

   printf("First process exit\n");

   return 0;
}