#ifndef MERGESORT_H
#define MERGESORT_H

#include <vector>

// Структура для возврата метрики времени
struct SortResult {
    double time_sec;
};

// Главная функция многопоточной сортировки слиянием
SortResult parallel_merge_sort(std::vector<double>& arr, int num_threads);

#endif // MERGESORT_H