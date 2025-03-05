#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
   int fd;

   char resstring[20] = "";

   char name[] = "./my_fifo.fifo";
   
   /* Second process */

   if((fd = open(name, O_RDONLY)) < 0){
      printf("Can\'t open FIFO for writting\n");
   exit(-1);
   }

   if(read(fd, resstring, sizeof(resstring)) != sizeof(resstring)){
      printf("Can\'t write all string to FIFO\n");
      exit(-1);
   }

   if(close(fd) < 0)
   {
      printf("Can\'t close FIFO to write\n");
      exit(-1);
   }

   printf("Second process exit, resstring: %s\n", resstring);

   return 0;
}