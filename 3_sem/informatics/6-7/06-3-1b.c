#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>

#define CURRENT_PROCESS 1

//#define DEBUG

#ifdef DEBUG
   #define prn fprintf(stderr, "%d: %s\n", __LINE__, __func__);
#else
   #define prn
#endif

int main()
{
   prn
   int *   array;
   int *   ready;
   int *   turn;

   int     shmid;

   int     array_new = 1,  // флаги инициализации 
           ready_new = 1, 
           turn_new = 1;

   char    pathname[] = "06-3a.c";

   key_t   key;
   
   long    i;

   // включаем array
   if((key = ftok(pathname,0)) < 0){
     printf("Can\'t generate key\n");
     exit(-1);
   }

   if((shmid = shmget(key, 3*sizeof(int), 0666|IPC_CREAT|IPC_EXCL)) < 0){

      if(errno != EEXIST){
         printf("Can\'t create shared memory\n");
         exit(-1);
      } else {
         if((shmid = shmget(key, 3*sizeof(int), 0)) < 0){
            printf("Can\'t find shared memory\n");
            exit(-1);
	 }
         array_new = 0;
      }
   }

   if((array = (int *)shmat(shmid, NULL, 0)) == (int *)(-1)){
      printf("Can't attach shared memory\n");
      exit(-1);
   }



   // включаем ready
   if((key = ftok(pathname,1)) < 0){
     printf("Can\'t generate key\n");
     exit(-1);
   }

   if((shmid = shmget(key, 2*sizeof(int), 0666|IPC_CREAT|IPC_EXCL)) < 0){

      if(errno != EEXIST){
         printf("Can\'t create shared memory\n");
         exit(-1);
      } else {
         if((shmid = shmget(key, 2*sizeof(int), 0)) < 0){
            printf("Can\'t find shared memory\n");
            exit(-1);
	 }
         ready_new = 0;
      }
   }

   if((ready = (int *)shmat(shmid, NULL, 0)) == (int *)(-1)){
      printf("Can't attach shared memory\n");
      exit(-1);
   }


   //включаем turn  
   if((key = ftok(pathname,2)) < 0){
     printf("Can\'t generate key\n");
     exit(-1);
   }

   if((shmid = shmget(key, 1*sizeof(int), 0666|IPC_CREAT|IPC_EXCL)) < 0){

      if(errno != EEXIST){
         printf("Can\'t create shared memory\n");
         exit(-1);
      } else {
         if((shmid = shmget(key, 1*sizeof(int), 0)) < 0){
            printf("Can\'t find shared memory\n");
            exit(-1);
	 }
         turn_new = 0;
      }
   }

   if((turn = (int *)shmat(shmid, NULL, 0)) == (int *)(-1)){
      printf("Can't attach shared memory\n");
      exit(-1);
   }


   // выполняем программу

   if(array_new && ready_new){
      array[0] =  0;
      array[1] =  1;
      array[2] =  1;

      ready[0] = 0;
      ready[1] = 0; 
   } else {
      prn
      ready[CURRENT_PROCESS] = 1; 

      prn
      turn[0] = 1 - CURRENT_PROCESS;
      prn

      while(ready[1-CURRENT_PROCESS] && turn[0] == 1-CURRENT_PROCESS); 

      //printf("ready[1-...] = %d, turn[0] = %d\n", ready[1-CURRENT_PROCESS], turn[0]);

      prn
   
      array[1] += 1;

      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      for(i=0; i<2000000000L; i++);
      
      array[2] += 1;
   }
 
   printf("Program 1 was spawn %d times, program 2 - %d times, total - %d times\n",
      array[0], array[1], array[2]);

   ready[CURRENT_PROCESS] = 0; 

   if(shmdt(array) < 0){
      printf("Can't detach shared memory\n");
      exit(-1);
   }

   return 0;
}
