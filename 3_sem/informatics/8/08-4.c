#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>
#include <errno.h>
#include <sys/sem.h>
#include <string.h>

#define N 100


#define prn fprintf(stderr, "%d: %s\n", __LINE__, __func__);

int main()
{
   int     fd[2], result;

   char   msg_from_p[14];
   char   msg_from_c[15];

   int semid;

   key_t key;

   char    pathname[] = "08-4.c";

   struct sembuf P0, V0, P1, V1;

   P0.sem_flg = 0;   // контролирует ребенка
   P0.sem_num = 0;
   P0.sem_op = -1;

   V0.sem_flg = 0;
   V0.sem_num = 0;
   V0.sem_op =  1;

   P1.sem_flg = 0;   // контролирует родителя
   P1.sem_num = 1;
   P1.sem_op = -1;

   V1.sem_flg = 0;
   V1.sem_num = 1;
   V1.sem_op =  1;

   key = ftok(pathname, 0);
    
    if((semid = semget(key, 2, 0666 | IPC_CREAT)) < 0){
      printf("Can\'t create semaphore set\n");
      exit(-1);
    }

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
      
    for (int i = 0; i < N; i++)
    {  
        printf("%d\n", i + 1);
        if(write(fd[1], "Hello, Child!", 14) != 14) 
        {
            prn
            perror("write");
            exit(-1);
        }

        printf("Parrent write: Hello, Child!\n");


        semop(semid, &V0, 1); // разрешаем ребенку читать сообщение, сам он при этом устанавливает семафор в 0

        semop(semid, &P1, 1); // блокируем процесс, ждем, пока ребенок отправит ответное сообщение
        
        if(read(fd[0], msg_from_c, 15) < 0)
        {
            prn
            perror("read");
            exit(-1);
        }

        printf("Parent read: %s\n\n", msg_from_c);
    }
      

      close(fd[1]);
      close(fd[0]);

      semop(semid, &V0, 1);
      printf("Parent exit\n");

   } else {

      /* Child process */


    for (int i = 0; i < N; i++)
    {
        semop(semid, &P0, 1);  // блокируем процесс, пока родитель не отправил сообщение
        
        if(read(fd[0], msg_from_p, 14) < 0)
        {
            prn
            perror("read");
            exit(-1);
        }

        printf("Child read: %s\n", msg_from_p);

        if(write(fd[1], "Hello, Parent!", 15) != 15) 
        {
            prn
            perror("write");
            exit(-1);
        }

        printf("Child write: Hello, Parent!\n");

        semop(semid, &V1, 1);   // разрешаем родителю читать отправленное сообщение, сам родитель устанавливает семафор в 0


        
    }
  


      close(fd[1]);
      close(fd[0]);

      semop(semid, &P0, 1);
      printf("Child exit\n");
   }

  semctl(semid, 0, IPC_RMID, 0);
  semctl(semid, 1, IPC_RMID, 0);

   return 0;
}