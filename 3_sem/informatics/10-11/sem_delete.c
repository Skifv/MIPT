#include <stdio.h>
#include <stdlib.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/sem.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/mman.h>

// функция, которая создает семафор по pathname и project_id, 
// инициализирует его init_value, и возвращает его идентификатор
int get_sem(char *pathname, int project_id, int init_value);

int main(void)
{
    char pathname[] = "11.3a.c";

    int sem_mutax_id = get_sem(pathname, 0, 1);
    int sem_wait_a_id = get_sem(pathname, 3, 0);
    int sem_wait_b_id = get_sem(pathname, 4, 0);

    semctl(sem_mutax_id, 0, IPC_RMID, 0);
    semctl(sem_wait_a_id, 0, IPC_RMID, 0);
    semctl(sem_wait_b_id, 0, IPC_RMID, 0);

    printf("Deleted\n");

    return 0;
}



int get_sem(char *pathname, int project_id, int init_value) 
{
    key_t key;
    int new = 1;

    key = ftok(pathname, project_id);
    if (key == -1) {
        perror("ftok");
        exit(EXIT_FAILURE);
    }

    int sem_id = semget(key, 1, 0666 | IPC_CREAT | IPC_EXCL);
    if (sem_id == -1) {
        if (errno != EEXIST) {
            perror("semget");
            exit(EXIT_FAILURE);
        }

        sem_id = semget(key, 1, 0);
        if (sem_id == -1) {
            perror("semget");
            exit(EXIT_FAILURE);
        }

        new = 0;
    }

    if (new) {
        int return_value = semctl(sem_id, 0, SETVAL, init_value);  
        if (return_value == -1) {
            perror("semctl");
            exit(EXIT_FAILURE);
        }
    }

    return sem_id;
}