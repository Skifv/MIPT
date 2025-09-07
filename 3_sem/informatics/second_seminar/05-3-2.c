#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h> // Для wait()

int main() {
    int fd1[2], fd2[2], result;
    size_t size;
    char parent_message[] = "Message from parent!";
    char child_message[] = "Message from child!";
    char buffer[25];

    // Создание двух труб
    if (pipe(fd1) < 0 || pipe(fd2) < 0) {
        printf("Can't open pipes\n");
        exit(-1);
    }

    result = fork();

    if (result < 0) {
        printf("Can't fork child\n");
        exit(-1);
    } else if (result > 0) {
        // Родительский процесс (пишет в первую трубу, читает из второй)
        close(fd1[0]);  
        close(fd2[1]);  

        // Отправляем сообщение дочернему процессу
        size = write(fd1[1], parent_message, sizeof(parent_message));
        if (size != sizeof(parent_message)) {
            printf("Can't write all string to pipe\n");
            exit(-1);
        }
        close(fd1[1]);

        // Ожидаем завершения дочернего процесса
        wait(NULL);

        // Читаем ответ от дочернего процесса
        size = read(fd2[0], buffer, sizeof(child_message));
        if (size < 0) {
            printf("Can't read string from pipe\n");
            exit(-1);
        }
        printf("Parent received: %s\n", buffer);

        close(fd2[0]);  

    } else {
        // Дочерний процесс (читает из первой трубы, пишет во вторую)
        close(fd1[1]);  
        close(fd2[0]);  

        // Читаем сообщение от родителя
        size = read(fd1[0], buffer, sizeof(parent_message));
        if (size < 0) {
            printf("Can't read string from pipe\n");
            exit(-1);
        }
        printf("Child received: %s\n", buffer);
        close(fd1[0]);

        // Отправляем ответ родительскому процессу
        size = write(fd2[1], child_message, sizeof(child_message));
        if (size != sizeof(child_message)) {
            printf("Can't write all string to pipe\n");
            exit(-1);
        }
        close(fd2[1]);
    }

    return 0;
}
