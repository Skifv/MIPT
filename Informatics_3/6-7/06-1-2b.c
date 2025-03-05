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

   if((key = ftok(pathname,0)) < 0){
     printf("Can\'t generate key\n");
     exit(-1);
   }

   if((shmid = shmget(key, N*sizeof(char), 0666)) < 0){
    perror("shmid");
    printf("Can\'t create shared memory\n");
    exit(-1);
   }

   if((array = (char *)shmat(shmid, NULL, 0)) == (char *)(-1)){
      printf("Can't attach shared memory\n");
      exit(-1);
   }

   printf("%s\n", array);

   shmctl(shmid, IPC_RMID, 0);

   return 0;
}
