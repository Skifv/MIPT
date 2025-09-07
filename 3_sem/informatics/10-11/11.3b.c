/*
    Задача повышенной сложности: напишите две программы, 
    использующие memory mapped файл для обмена информацией при 
    одновременной работе, подобно тому, как они могли бы использовать 
    разделяемую память.
*/

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

#define BUFFER_SIZE 64  // Размер буфера для обмена сообщениями
#define N 10  // Количество сообщений, которое будет обработано

// Структуры для операций над семафорами
struct sembuf P, V;

// Функция для создания и инициализации семафора
int get_sem(char *pathname, int project_id, int init_value);

int main(void)
{
    // Путь к файлу для генерации ключа для семафора
    char pathname[] = "11.3a.c";

    // Получаем идентификаторы семафоров для синхронизации процессов
    int sem_mutax_id = get_sem(pathname, 0, 1);  // Семафор для контроля доступа к критической секции
    int sem_wait_a_id = get_sem(pathname, 3, 0);  // Семафор для ожидания сообщения от процесса A
    int sem_wait_b_id = get_sem(pathname, 4, 0);  // Семафор для уведомления процесса A, что B готово работать

    // Инициализация операций над семафорами (операции P и V)
    P.sem_num = 0;
    P.sem_op = -1;  // Операция захвата семафора (уменьшение)
    P.sem_flg = 0;
    
    V.sem_num = 0;
    V.sem_op = 1;  // Операция освобождения семафора (увеличение)
    V.sem_flg = 0;

    // Путь к файлу для обмена данными между процессами
    char * buffer_path = "./buffers/buffer.txt";
    
    // Открытие файла для чтения и записи, создание файла, если он не существует
    int fd = open(buffer_path, O_RDWR | O_CREAT, 0666);
    if (fd == -1) 
    {
        perror("open");
        exit(EXIT_FAILURE);
    }

    // Установка размера файла
    ftruncate(fd, BUFFER_SIZE);

    // Отображаем файл в память для обмена данными между процессами
    char * buffer = mmap(NULL, BUFFER_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (buffer == MAP_FAILED) 
    {
        perror("mmap");
        exit(EXIT_FAILURE);
    }

    // Закрываем дескриптор файла, так как он больше не нужен
    close(fd);

    // Переменная для хранения сообщения
    char message[BUFFER_SIZE];

    // Цикл для обработки сообщений
    for (int i = 1; i <= N; i++)
    {    
        // Ожидание сообщения от процесса A
        semop(sem_wait_a_id, &P, 1);    
        
        // Захват семафора для критической секции
        semop(sem_mutax_id, &P, 1);

        // Вывод полученного сообщения от процесса A
        printf("B. Message from A: %s\n", buffer);

        // Формирование и запись ответа для процесса A
        snprintf(message, BUFFER_SIZE, "B. Hello, A! %d", i);
        strncpy(buffer, message, BUFFER_SIZE);

        // Освобождение семафора для критической секции
        semop(sem_mutax_id, &V, 1);
        
        // Уведомление процесса A, что ответ отправлен
        semop(sem_wait_b_id, &V, 1);
    }

    // Отмэппинг буфера, завершение работы с памятью
    munmap(buffer, BUFFER_SIZE);
    return 0;
}

// Функция для получения идентификатора семафора и его инициализации
int get_sem(char *pathname, int project_id, int init_value) 
{
    key_t key;
    int new = 1;

    // Генерация ключа для семафора с использованием пути к файлу и project_id
    key = ftok(pathname, project_id);
    if (key == -1) {
        perror("ftok");
        exit(EXIT_FAILURE);
    }

    // Попытка получить семафор с созданием, если он не существует
    int sem_id = semget(key, 1, 0666 | IPC_CREAT | IPC_EXCL);
    if (sem_id == -1) {
        if (errno != EEXIST) {
            perror("semget");
            exit(EXIT_FAILURE);
        }

        // Если семафор уже существует, получаем его идентификатор
        sem_id = semget(key, 1, 0);
        if (sem_id == -1) {
            perror("semget");
            exit(EXIT_FAILURE);
        }

        new = 0;
    }

    // Инициализация семафора, если это новый семафор
    if (new) {
        int return_value = semctl(sem_id, 0, SETVAL, init_value);  
        if (return_value == -1) {
            perror("semctl");
            exit(EXIT_FAILURE);
        }
    }

    return sem_id;
}
