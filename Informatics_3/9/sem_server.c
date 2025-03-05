#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/shm.h>
#include <errno.h>

#if 1
#define prn fprintf(stderr, "%d: %s\n", __LINE__, __func__);
#else
#define prn
#endif

#define SERVER 1
#define N 100

#define V 1
#define P 2

// Структура для элемента очереди
typedef struct QueueNode {
    long int client_id;         // Идентификатор клиента
    int semaphore_number;  // Номер семафора
    struct QueueNode* next;
} QueueNode;

// Структура для самой очереди
typedef struct Queue {
    QueueNode* front;  // Указатель на начало очереди
    QueueNode* rear;   // Указатель на конец очереди
} Queue;



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

Queue* createQueue();
void enqueue(Queue* q, int client_id, int semaphore_number);
int dequeue(Queue* q, int* client_id, int* semaphore_number);
int isQueueEmpty(Queue* q);
void freeQueue(Queue* q);

int removeNode(Queue* q, int client_id, int* semaphore_number);
int find_client(Queue* q, int sem_id, long int* client_id);

int main(void)
{
    // Get the message queue for communication with clients
    char pathname[] = "sem_server.c";
    int project_id = 0;

    int msqid = get_message_queue(pathname, project_id);

    // Structure to hold messages from clients
    struct client client_message;
    // Structure to hold messages from clients
    struct server server_message;

    // Create a queue to hold the id's and semaphore numbers of processes waiting for a resource
    Queue* queue = createQueue();

    printf("Server is on, waiting requests.\n");

    while(1)
    {
        // Get the next message from a client
        if((msgrcv(msqid, (struct msgbuf *) &client_message, sizeof(client_message.message), SERVER, 0)) < 0){
            perror("msgrcv");
            exit(-1);
        }
        // attach sem по его id
        if ((client_message.message.semaphore = (unsigned int *) shmat(client_message.message.shmid, NULL, 0)) == (void *) -1) {
            perror("shmat");
            exit(-1);
        }

        // If the operation is V, increment the semaphore value and send a response back to the client
        if (client_message.message.sem_op == V) {
            printf("Got request from client %ld: V(%d)\n", client_message.message.id, client_message.message.shmid);

            *(client_message.message.semaphore) += 1;

            server_message.mtype = client_message.message.id;

            if ((msgsnd(msqid, (struct msgbuf *) &server_message, 0, 0)) < 0){
                perror("msgsnd");
                exit(-1);
            }

            printf("Request from client %ld processed. \n", client_message.message.id);

            // If some client with sem was waiting in the queue, remove it
            if (find_client(queue, client_message.message.shmid, &client_message.message.id))
            {
                removeNode(queue, client_message.message.id, &client_message.message.shmid);

                *(client_message.message.semaphore) -= 1;

                server_message.mtype = client_message.message.id;

                if ((msgsnd(msqid, (struct msgbuf *) &server_message, 0, 0)) < 0){
                    perror("msgsnd");
                    exit(-1);
                }

                printf("Request from client %ld processed. \n", client_message.message.id);
            }

            // deteach sem если он не равен NULL
            if (client_message.message.semaphore != NULL) 
            {
                if (shmdt(client_message.message.semaphore) < 0) 
                {
                    perror("shmdt");
                    exit(-1);
                }
                client_message.message.semaphore = NULL;
            }

        }
        // If the operation is P, decrement the semaphore value if possible and send a response back to the client
        else if (client_message.message.sem_op == P) {
            printf("Got request from client %ld: P(%d)\n", client_message.message.id, client_message.message.shmid);

            // If the semaphore value is greater than 0, decrement it and send a response back to the client
            if (*(client_message.message.semaphore) > 0) 
            {
                *(client_message.message.semaphore) -= 1;

                server_message.mtype = client_message.message.id;

                if ((msgsnd(msqid, (struct msgbuf *) &server_message, 0, 0)) < 0){
                    perror("msgsnd");
                    exit(-1);
                }

                printf("Request from client %ld processed. \n", client_message.message.id);

                // deteach sem
                if (shmdt(client_message.message.semaphore) < 0) {
                    perror("shmdt");
                    exit(-1);
                }
                client_message.message.semaphore = NULL;
            }
            // Otherwise, add the client to the waiting queue
            else {
                enqueue(queue, client_message.message.id, client_message.message.shmid);
            }
        }
    }

    return 0;    
}

// Функция для поиска первого клиента с семафором client_message->sem.shmid в очереди семафоров
int find_client(Queue* q, int sem_id, long int* client_id)
{ 
    if (q->front == NULL) {
        return 0; // Очередь пуста
    }

    QueueNode* current = q->front;

    // Проходим по очереди
    while (current != NULL) {
        if (current->semaphore_number == sem_id) {
            if (client_id != NULL) {
                *client_id = current->client_id;
            }
            return 1; // Найден клиент с данным sem_id
        }
        current = current->next;
    }

    return 0; // Клиент с таким sem_id не найден
}


// Функция для создания новой очереди
Queue* createQueue() {
    Queue* q = (Queue*)malloc(sizeof(Queue));
    if (!q) {
        perror("Failed to allocate memory for queue");
        exit(EXIT_FAILURE);
    }
    q->front = NULL;
    q->rear = NULL;
    return q;
}

// Функция для добавления элемента в очередь
void enqueue(Queue* q, int client_id, int semaphore_number) {
    QueueNode* newNode = (QueueNode*)malloc(sizeof(QueueNode));
    if (!newNode) {
        perror("Failed to allocate memory for queue node");
        exit(EXIT_FAILURE);
    }
    newNode->client_id = client_id;
    newNode->semaphore_number = semaphore_number;
    newNode->next = NULL;

    if (q->rear) {
        q->rear->next = newNode;
    } else {
        q->front = newNode;
    }
    q->rear = newNode;
}

// Функция для удаления элемента из очереди
int dequeue(Queue* q, int* client_id, int* semaphore_number) {
    if (!q->front) {
        return 0; // Очередь пуста
    }

    QueueNode* temp = q->front;
    *client_id = temp->client_id;
    *semaphore_number = temp->semaphore_number;

    q->front = temp->next;
    if (!q->front) {
        q->rear = NULL;
    }
    free(temp);
    return 1; // Успешное удаление
}

int removeNode(Queue* q, int client_id, int* semaphore_number) {
    if (q->front == NULL) {
        return 0; // Очередь пуста
    }

    QueueNode* current = q->front;
    QueueNode* previous = NULL;

    // Ищем узел с заданным client_id
    while (current != NULL && current->client_id != client_id) {
        previous = current;
        current = current->next;
    }

    if (current == NULL) {
        return 0; // Узел с таким client_id не найден
    }

    // Сохраняем номер семафора
    if (semaphore_number != NULL) {
        *semaphore_number = current->semaphore_number;
    }

    // Если узел — это первый элемент
    if (previous == NULL) {
        q->front = current->next;
    } else {
        previous->next = current->next;
    }

    // Если узел — это последний элемент
    if (current == q->rear) {
        q->rear = previous;
    }

    free(current);
    return 1; // Успешное удаление
}


// Функция для проверки, пуста ли очередь
int isQueueEmpty(Queue* q) {
    return q->front == NULL;
}

// Освобождение памяти, выделенной для очереди
void freeQueue(Queue* q) {
    while (!isQueueEmpty(q)) {
        int client_id, semaphore_number;
        dequeue(q, &client_id, &semaphore_number);
    }
    free(q);
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


