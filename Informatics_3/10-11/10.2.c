/*
    Задача повышенной сложности: напишите программу, 
    распечатывающую содержимое заданного каталога в формате, 
    аналогичном формату выдачи команды ls -al.
*/

#include <sys/types.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>
#include <pwd.h>
#include <grp.h>

#define INITIAL_FILE_COUNT 64  // Начальный размер массива структур из файлов директории
#define MAX_PATH 1024          // Максимальная длина пути к файлу/каталогу

// Структура для хранения информации о файле
struct myfile {
    char *name;       
    struct stat st;   
};

// Функция для подсчета количества цифр в числе
int count_digits(unsigned long long number) {
    int digit_count = 0;
    do {
        digit_count++;
        number /= 10;
    } while (number);
    return digit_count;
}

// Функция для определения типа файла (каталог, обычный файл и т.д.)
char get_file_type(mode_t mode) {
    if (S_ISDIR(mode)) return 'd';  // Каталог
    if (S_ISREG(mode)) return '-';  // Обычный файл
    if (S_ISCHR(mode)) return 'c';  // Символьный файл
    if (S_ISBLK(mode)) return 'b';  // Блочный файл
    if (S_ISFIFO(mode)) return 'p'; // Канал (FIFO)
    if (S_ISLNK(mode)) return 'l';  // Символьная ссылка
    return '?';                     // Неизвестный тип
}

// Функция для получения прав доступа к файлу в виде строки
char *get_file_access(mode_t mode) {
    static char access[10];  
    access[0] = (mode & S_IRUSR) ? 'r' : '-';
    access[1] = (mode & S_IWUSR) ? 'w' : '-';
    access[2] = (mode & S_IXUSR) ? 'x' : '-';
    access[3] = (mode & S_IRGRP) ? 'r' : '-';
    access[4] = (mode & S_IWGRP) ? 'w' : '-';
    access[5] = (mode & S_IXGRP) ? 'x' : '-';
    access[6] = (mode & S_IROTH) ? 'r' : '-';
    access[7] = (mode & S_IWOTH) ? 'w' : '-';
    access[8] = (mode & S_IXOTH) ? 'x' : '-';
    access[9] = '\0'; 
    return access;
}

int main(int argc, char *argv[]) {
    if (argc > 2) {
        fprintf(stderr, "Usage: %s [directory]\n", argv[0]);
        exit(EXIT_FAILURE);  
    }

    char *pathname = (argc == 1) ? "." : argv[1];
    DIR *directory = opendir(pathname);
    if (!directory) {
        perror("Can't open directory");  
        exit(EXIT_FAILURE);
    }

    // Инициализируем динамический массив для хранения информации о файлах в виде структур
    int capacity = INITIAL_FILE_COUNT;  // Начальный размер массива
    struct myfile *files_stat = malloc(capacity * sizeof(struct myfile));
    if (!files_stat) {
        perror("Memory allocation failed");  
        closedir(directory);
        exit(EXIT_FAILURE);
    }

    int count = 0;          // Счетчик количества прочитанных директорий
    nlink_t max_links = 1;  // Максимальное количество жестких ссылок
    off_t max_size = 1;     // Максимальный размер файла

    struct dirent *entry = NULL;  // Переменная для хранения записи о файле

    while (entry = readdir(directory)) {
        char full_path[MAX_PATH];
        snprintf(full_path, sizeof(full_path), "%s/%s", pathname, entry->d_name);

        struct stat stat_buffer;  // Буфер для хранения информации о файле/каталоге]
        if (stat(full_path, &stat_buffer) == -1) {
            perror("stat");  
            free(files_stat);
            closedir(directory);
            exit(EXIT_FAILURE);
        }

        // Увеличиваем размер массива, если нужно
        if (count >= capacity) {
            capacity *= 2;  
            files_stat = realloc(files_stat, capacity * sizeof(struct myfile));
            if (!files_stat) {
                perror("Memory allocation failed"); 
                closedir(directory);
                exit(EXIT_FAILURE);
            }
        }

        // Сохраняем информацию о файле в массив
        files_stat[count].st = stat_buffer;
        files_stat[count].name = entry->d_name;

        // Обновляем максимальные значения количества ссылок и размера
        if (stat_buffer.st_nlink > max_links) max_links = stat_buffer.st_nlink;
        if (stat_buffer.st_size > max_size) max_size = stat_buffer.st_size;

        count++;  // Увеличиваем счетчик файлов
    }

    // Вычисляем количество цифр для вывода максимальных значений
    int len_max_links = count_digits(max_links);
    int len_max_size  = count_digits(max_size);

    
    for (int i = 0; i < count; i++) {
        // Получаем строку с правами доступа и временем последней модификации
        char *current_file_access = get_file_access(files_stat[i].st.st_mode);
        char *buf_time = ctime(&files_stat[i].st.st_mtime);
        buf_time[strlen(buf_time) - 1] = '\0';  // Удаляем символ новой строки


        printf("%c", get_file_type(files_stat[i].st.st_mode));      // Тип файла
        printf("%s", current_file_access);                          // Права доступа
        printf(" %*lu", len_max_links, files_stat[i].st.st_nlink);  // Количество жестких ссылок
        printf(" %s", getpwuid(files_stat[i].st.st_uid)->pw_name);  // Имя владельца файла
        printf(" %s", getgrgid(files_stat[i].st.st_gid)->gr_name);  // Имя группы
        printf(" %*ld", len_max_size, files_stat[i].st.st_size);    // Размер файла
        printf(" %s", buf_time);                                    // Время последней модификации
        printf(" %s\n", files_stat[i].name);                        // Имя файла
    }

    free(files_stat);
    closedir(directory);
    return 0;
}
