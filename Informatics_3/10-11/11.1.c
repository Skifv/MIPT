/*
    Откомпилируйте и прогоните программу 11-1.с, которая создает файл, 
    отображает его в адресное пространство процесса и заносит в него 
    информацию с помощью обычных операций языка С.
*/

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    // Переменные для файлового дескриптора и длины отображаемого файла
	int fd;
	size_t length;
    int i;

    // Определение структуры для хранения данных
	struct A {
        double f;  
        double f2; 
    } *ptr, *tmpptr;

	fd = open("mapped.dat", O_RDWR | O_CREAT, 0666);
	if (fd == -1) {
		printf("File open failed!\n"); 
		exit(EXIT_FAILURE); 
	}

    length = 100000 * sizeof(struct A);

    // Устанавливаем размер файла с помощью ftruncate (необходимо, иначе при попытке записи сигфолт)
    ftruncate(fd, length);

    // Отображаем файл в память 
	ptr = (struct A *)mmap(NULL, length, PROT_WRITE | PROT_READ, MAP_SHARED, fd, 0);
    close(fd);
	if (ptr == MAP_FAILED) {
		printf("Mapping failed!\n"); 
		exit(EXIT_FAILURE); 
	}

    tmpptr = ptr;
    for (i = 1; i <= 100000; i++) {
        tmpptr->f = i;          
        tmpptr->f2 = tmpptr->f * tmpptr->f; 
        tmpptr++;  
    }

    munmap((void *)ptr, length);
    return 0; 
}
