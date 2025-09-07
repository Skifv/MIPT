#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#define N 10000

int main() 
{ 
   char *  array;   // передаваемая строка
   int     shmid;   // возвращаемое значение shmget
   char    pathname[] = "06-1-2a.c"; 
   key_t   key;     // ключ для файла
   FILE * file_read;

   char buffer[N];
 
   if((file_read = (FILE *)fopen(pathname, "r")) < 0)
   {
      perror("fopen");
      exit(EXIT_FAILURE);
   }

   int i = 0;
   while((i < N) && (fscanf(file_read, "%c", &buffer[i]) != EOF))
   {
      i++;
   }

   if(i >= N)
   {
      perror("i >= N");
      exit(EXIT_FAILURE);
   }

   //printf("%s", buffer);
   

   if((key = ftok(pathname,0)) < 0){
     printf("Can\'t generate key\n");
     exit(-1);
   }

   if((shmid = shmget(key, N*sizeof(char), 0666|IPC_CREAT)) < 0){
    printf("Can\'t create shared memory\n");
    exit(-1);
   }

   if((array = (char *)shmat(shmid, NULL, 0)) == (char *)(-1)){
      printf("Can't attach shared memory\n");
      exit(-1);
   }

   char * string = &buffer[0];

   memcpy(array, string, strlen(string) + 1);

   if(shmdt(array) < 0){
      printf("Can't detach shared memory\n");
      exit(-1);
   }


   return 0;
}