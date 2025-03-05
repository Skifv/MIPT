/*
    Модифицируйте предыдущую программу (11-1.с) так, чтобы она 
    отображала файл, записанный этой программой, в память и считала 
    сумму квадратов чисел от 1 до 100000, которые уже находятся в этом 
    файле.
*/

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <pwd.h>
#include <grp.h>

// Определяем константу для количества структур в файле
#define N_STRTUCTS 100000


struct A 
{
    double f;   
    double f1;  
};

int main(void)
{
    char * pathname = "mapped.dat";
    
    int fd = open(pathname, O_RDWR);
    if (fd == -1) 
    {
        perror("open"); 
        exit(EXIT_FAILURE); 
    }
    
    // Проверяем информацию о файле, чтобы убедиться, что он имеет правильный размер
    struct stat stat_buffer; 
    if(fstat(fd, &stat_buffer) < 0) 
    {
        perror("fstat"); 
        close(fd);       
        exit(EXIT_FAILURE); 
    }

    // Рассчитываем ожидаемый размер файла
    size_t length = N_STRTUCTS * sizeof(struct A);
    if (stat_buffer.st_size != length) // Проверяем, совпадает ли реальный размер файла с ожидаемым
    {
        printf("Wrong file size. Expected %zd, got %zd\n", length, stat_buffer.st_size); 
        close(fd); 
        exit(EXIT_FAILURE); 
    }
    
    // Отображаем файл в память
    struct A * ptr = mmap(NULL, length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ptr == MAP_FAILED) 
    {
        perror("mmap"); 
        close(fd);     
        exit(EXIT_FAILURE); 
    }
    close(fd);  

    // Создаем указатель на начало отображенного файла
    struct A * tmpptr = ptr;
    unsigned long long int sum = 0; 
    for (int i = 1; i <= N_STRTUCTS; i++) 
    {
        sum += tmpptr->f1; 
        tmpptr++;
    }

    // Освобождаем отображенную память
    munmap(ptr, length);

    // Выводим результат вычисления суммы
    printf("sum = %llu\n", sum);

    return 0; 
}
