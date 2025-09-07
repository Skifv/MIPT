#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/sem.h>

#define prn fprintf(stderr, "%d: %s\n", __LINE__, __func__);

int main()
{
    int *array;
    int shmid;
    int new = 1, new_sem = 1;
    char pathname[] = "08-2a.c";
    key_t key;
    long i;

    int semnum = 0; // Номер семафора в наборе
    int semval;

    int semid;
    struct sembuf V, P;

    V.sem_num = 0;
    V.sem_op = 1;
    V.sem_flg = 0;

    P.sem_num = 0;
    P.sem_op = -1;
    P.sem_flg = 0;

    if ((key = ftok(pathname, 0)) < 0)
    {
        printf("Can\'t generate key\n");
        exit(-1);
    }

    if ((semid = semget(key, 1, 0)) < 0)
    {

        prn
            perror("semget");
        exit(-1);
    }

    semval = semctl(semid, semnum, GETVAL);
    if (semval == -1)
    {
        perror("semctl GETVAL");
    }
    else
    {
        printf("Текущее значение семафора: %d\n", semval);
    }

    return 0;
}