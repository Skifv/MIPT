#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>

int main()
{
   int     shmid;

   char    pathname[] = "06-3a.c";

   key_t   key;

   // включаем array
   if((key = ftok(pathname,0)) < 0){
     printf("Can\'t generate key\n");
     exit(-1);
   }

   if((shmid = shmget(key, 3*sizeof(int), 0)) < 0){
            printf("Can\'t find shared memory\n");
            exit(-1);
   }

   shmctl(shmid, IPC_RMID, 0);

   // включаем ready
   if((key = ftok(pathname,1)) < 0){
     printf("Can\'t generate key\n");
     exit(-1);
   }

  if((shmid = shmget(key, 2*sizeof(int), 0)) < 0){
            printf("Can\'t find shared memory\n");
            exit(-1);
	 }

   shmctl(shmid, IPC_RMID, 0);



   //включаем turn  
   if((key = ftok(pathname,2)) < 0){
     printf("Can\'t generate key\n");
     exit(-1);
   }

   if((shmid = shmget(key, 1*sizeof(int), 0)) < 0){
            printf("Can\'t find shared memory\n");
            exit(-1);
	}

    shmctl(shmid, IPC_RMID, 0);
}