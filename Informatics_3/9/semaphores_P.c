#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/shm.h>
#include <errno.h>

#if 0
#define prn fprintf(stderr, "%d: %s\n", __LINE__, __func__);
#else
#define prn
#endif

#define SERVER 1
#define N 100

#define V 1
#define P 2

struct Semaphore
{
    int shmid;
    unsigned int *semaphore;
};

/* Схема клиент-сервер */

    struct client 
    {
        long mtype;              // всегда SERVER   
        struct {
            long id;             // id процесса-клиента

            unsigned int sem_op; // V - V(S), P - P(S)
            int shmid;
            unsigned int *semaphore;
        } message;
    };

    struct server 
    {
        long mtype;

        int message;
   };

int get_message_queue(char *pathname, int project_id);
struct Semaphore create_semaphore(char *pathname, int project_id, int init_value);

void sem_V(struct Semaphore *semaphore);
void sem_P(struct Semaphore *semaphore);


int main(void)
{ 
    char pathname[]="sem_server.c";
    int project_id = 0;

    // создание семафора
    int init_value = 1; 
    struct Semaphore sem = create_semaphore(pathname, project_id, init_value);

    printf("%d\n", *sem.semaphore);

    sem_P(&sem);
    
    printf("%d\n", *sem.semaphore);

    if(shmdt(sem.semaphore) < 0){
        perror("shmdt");
        exit(-1);
    }

    return 0;    
}


int get_message_queue(char *pathname, int project_id)
{
    key_t key = ftok(pathname, project_id);
    if (key == -1) {
        perror("ftok");
        exit(EXIT_FAILURE);
    }

    int msqid = msgget(key, IPC_CREAT | 0666);
    if (msqid == -1) {
        perror("msgget");
        exit(EXIT_FAILURE);
    }

    return msqid;
}

struct Semaphore create_semaphore(char *pathname, int project_id, int init_value)
{
    key_t key = ftok(pathname, project_id);
    if (key == -1) {
        perror("ftok");
        exit(EXIT_FAILURE);
    }

    int new = 1;
    int shm_id = shmget(key, sizeof(unsigned int), IPC_CREAT | IPC_EXCL | 0666);
    if (shm_id == -1) {
        if (errno != EEXIST) {
            perror("shmget");
            exit(EXIT_FAILURE);
        }

        shm_id = shmget(key, sizeof(unsigned int), 0);
        if (shm_id == -1) {
            perror("shmget");
            exit(EXIT_FAILURE);
        }

        new = 0;
    }

    unsigned int *semaphore = shmat(shm_id, NULL, 0);
    if (semaphore == (void *) -1) {
        perror("shmat");
        exit(EXIT_FAILURE);
    }

    struct Semaphore res = { .shmid = shm_id, .semaphore = semaphore };

    if(new) {
        *semaphore = init_value;
    }

    return res;
}

void sem_V(struct Semaphore *semaphore)
{
    char pathname[]="sem_server.c";
    int project_id = 0;

    // создание очереди сообщений
    int msqid = get_message_queue(pathname, project_id);

    // инициализация сообщения от клиента
    struct client client_msg;
    int client_id = getpid();
    client_msg.mtype = SERVER;
    client_msg.message.id = client_id;

    // само сообщение
    client_msg.message.sem_op = V;
    client_msg.message.shmid = semaphore->shmid;
    client_msg.message.semaphore = NULL;

    // сообщение от сервера
    struct server server_msg;

    // отправляемое сообщение
    if(msgsnd(msqid, (struct msgbuf *) &client_msg, sizeof(client_msg.message), 0) < 0){
       perror("msgsend");
       exit(-1);
    }

    // ждем ответа от сервера
    if(msgrcv(msqid, (struct msgbuf *) &server_msg, 0, client_id, 0) < 0){
        perror("msgrcv");
        exit(-1);
    }

    return;    
}

void sem_P(struct Semaphore *semaphore)
{
    char pathname[]="sem_server.c";
    int project_id = 0;

    // создание очереди сообщений
    int msqid = get_message_queue(pathname, project_id);

    // инициализация сообщения от клиента
    struct client client_msg;
    int client_id = getpid();
    client_msg.mtype = SERVER;
    client_msg.message.id = client_id;

    // само сообщение
    client_msg.message.sem_op = P;
    client_msg.message.shmid = semaphore->shmid;
    client_msg.message.semaphore = NULL;

    // сообщение от сервера
    struct server server_msg;

    // отправляемое сообщение
    if(msgsnd(msqid, (struct msgbuf *) &client_msg, sizeof(client_msg.message), 0) < 0){
       perror("msgsend");
       exit(-1);
    }

    // ждем ответа от сервера
    if(msgrcv(msqid, (struct msgbuf *) &server_msg, 0, client_id, 0) < 0){
        perror("msgrcv");
        exit(-1);
    }

    return;       
}
