#include <sys/types.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 100

int main()
{
   int     fd_out;
   char    res_string[N];
   int result;

   (void)umask(0);

   if(((fd_out = open("myfile", O_RDONLY | O_CREAT, 0666)) < 0)){
     printf("Can\'t open file\n");
     exit(-1);
   }

   if((result = read(fd_out, res_string, N)) != strlen(res_string) + 1){
     printf("Can\'t read string, %d\n", result);
     exit(-1);
   }

   if((close(fd_out) < 0)){
     printf("Can\'t close file");
   }
  
   printf("%s\n", res_string);

   return 0;
}