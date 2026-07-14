#include "mergesort.h"
#include <pthread.h>
#include <chrono>
#include <algorithm>

// Базовая функция слияния двух отсортированных частей [left, mid] и [mid+1, right]
// Использует общий вспомогательный массив temp для исключения лишних выделений памяти
void merge(std::vector<double>& arr, std::vector<double>& temp, int left, int mid, int right) {
    int i = left, j = mid + 1, k = left;
    
    // Слияние элементов
    while (i <= mid && j <= right) {
        if (arr[i] <= arr[j]) {
            temp[k++] = arr[i++];
        } else {
            temp[k++] = arr[j++];
        }
    }
    // Дописываем остатки
    while (i <= mid)   temp[k++] = arr[i++];
    while (j <= right) temp[k++] = arr[j++];
    
    // Копируем обратно в оригинальный массив
    for (i = left; i <= right; ++i) {
        arr[i] = temp[i];
    }
}

// Последовательная рекурсивная сортировка слиянием (работает внутри 1 потока)
void seq_merge_sort(std::vector<double>& arr, std::vector<double>& temp, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        seq_merge_sort(arr, temp, left, mid);
        seq_merge_sort(arr, temp, mid + 1, right);
        merge(arr, temp, left, mid, right);
    }
}

// Аргументы для потоков на этапе первоначальной сортировки
struct ThreadSortArgs {
    std::vector<double>* arr;
    std::vector<double>* temp;
    int left;
    int right;
};

void* thread_sort_routine(void* arg) {
    auto args = static_cast<ThreadSortArgs*>(arg);
    if (args->left < args->right) {
        seq_merge_sort(*(args->arr), *(args->temp), args->left, args->right);
    }
    return nullptr;
}

// Аргументы для потоков на этапе слияния блоков
struct ThreadMergeArgs {
    std::vector<double>* arr;
    std::vector<double>* temp;
    int left;
    int mid;
    int right;
};

void* thread_merge_routine(void* arg) {
    auto args = static_cast<ThreadMergeArgs*>(arg);
    merge(*(args->arr), *(args->temp), args->left, args->mid, args->right);
    return nullptr;
}

SortResult parallel_merge_sort(std::vector<double>& arr, int num_threads) {
    int n = arr.size();
    if (n <= 1) return {0.0};

    // Ограничиваем количество потоков размером массива (во избежание пустых блоков)
    num_threads = std::min(num_threads, n);

    auto start_time = std::chrono::high_resolution_clock::now();

    // Единый буфер, переиспользуемый на всех этапах. 
    // Поскольку куски массива в потоках не пересекаются, Data Race исключен.
    std::vector<double> temp(n);

    // ==========================================
    // ФАЗА 1: Независимая сортировка блоков
    // ==========================================
    std::vector<pthread_t> threads(num_threads);
    std::vector<ThreadSortArgs> sort_args(num_threads);

    for (int i = 0; i < num_threads; ++i) {
        sort_args[i].arr = &arr;
        sort_args[i].temp = &temp;
        sort_args[i].left = i * n / num_threads;
        // Последний элемент блока
        sort_args[i].right = (i + 1) * n / num_threads - 1;
        
        pthread_create(&threads[i], nullptr, thread_sort_routine, &sort_args[i]);
    }

    // Ждем завершения сортировки всех кусочков
    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], nullptr);
    }

    // ==========================================
    // ФАЗА 2: Попарное слияние (Merge Tree)
    // ==========================================
    // На каждом шаге размер сливаемых блоков удваивается
    int step = 1;
    while (step < num_threads) {
        std::vector<pthread_t> merge_threads;
        std::vector<ThreadMergeArgs> merge_args;

        // Идем по блокам с шагом 2*step
        for (int i = 0; i + step < num_threads; i += 2 * step) {
            ThreadMergeArgs m_arg;
            m_arg.arr = &arr;
            m_arg.temp = &temp;
            m_arg.left = i * n / num_threads;
            m_arg.mid = (i + step) * n / num_threads - 1;
            // Правый край может обрезаться границей массива
            m_arg.right = std::min((i + 2 * step) * n / num_threads - 1, n - 1);

            merge_args.push_back(m_arg);
        }

        // Запускаем независимые слияния пар
        merge_threads.resize(merge_args.size());
        for (size_t k = 0; k < merge_args.size(); ++k) {
            pthread_create(&merge_threads[k], nullptr, thread_merge_routine, &merge_args[k]);
        }

        // Ждем завершения текущего уровня слияния перед переходом к следующему укрупнению
        for (size_t k = 0; k < merge_threads.size(); ++k) {
            pthread_join(merge_threads[k], nullptr);
        }

        step *= 2;
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end_time - start_time;

    return {diff.count()};
}