#include <stdio.h>
#include <stdlib.h>
#include <sys/shm.h>
#include <sys/types.h>
#include <errno.h>
#include <stddef.h>

int main()
{
   int     *array;  // [0] - сколько раз был запущен 1 процесс, [1] - второй, [2] - оба
   int     shmid;   // возвращаемое значение shmget
   int     new = 1; // флаг инициализации массива
   char    pathname[] = "06-1a.c"; 
   key_t   key;     // ключ для файла

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
         new = 0;
      }
   }

   if((array = (int *)shmat(shmid, NULL, 0)) == (int *)(-1)){
      printf("Can't attach shared memory\n");
      exit(-1);
   }

   if(new){
      array[0] =  1;
      array[1] =  0;
      array[2] =  1;
   } else {
      array[0] += 1;
      array[2] += 1;
   }

   printf("Program 1 was spawn %d times, program 2 - %d times, total - %d times\n",
      array[0], array[1], array[2]);

   if(shmdt(array) < 0){
      printf("Can't detach shared memory\n");
      exit(-1);
   }

   return 0;
}
