#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>

#define BUF_SIZE 1

int main() {
    int fd[2];
    char buffer[BUF_SIZE];
    int total_written = 0;

    if (pipe(fd) == -1) {
        perror("pipe");
        return 1;
    }

    int flags = fcntl(fd[1], F_GETFL);
    fcntl(fd[1], F_SETFL, flags | O_NONBLOCK);

    while (1) {
        int bytes_written = write(fd[1], buffer, BUF_SIZE);
        if (bytes_written == -1) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                printf("Размер pipe: %d байт\n", total_written);
                break;
            } else {
                perror("write");
                return 1;
            }
        }
        total_written += bytes_written;
    }

    close(fd[0]);
    close(fd[1]);

    return 0;
}
