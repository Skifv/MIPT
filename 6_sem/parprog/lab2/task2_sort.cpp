#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include "mergesort.h"
#include <cstring>

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Использование: " << argv[0] << " <threads> <input.bin> <output.bin>\n";
        return 1;
    }

    int num_threads = std::stoi(argv[1]);
    std::string input_file = argv[2];
    std::string output_file = argv[3];

    std::ifstream in(input_file, std::ios::binary);
    if (!in) {
        std::cerr << "Ошибка: не удалось открыть файл.\n";
        return 1;
    }

    // Считываем весь файл в буфер байт
    std::vector<char> buffer((std::istreambuf_iterator<char>(in)), 
                              std::istreambuf_iterator<char>());
    in.close();

    // Создаем вектор double и просто копируем туда память из буфера
    std::vector<double> arr(buffer.size() / sizeof(double));
    if (!arr.empty()) {
        std::memcpy(arr.data(), buffer.data(), buffer.size());
    }

    int num_elements = arr.size();

    // Многопоточная сортировка
    SortResult res = parallel_merge_sort(arr, num_threads);
    std::cout << "MergeSort Time: " << res.time_sec << "\n";

    std::ofstream out(output_file, std::ios::binary);
    if (!out) {
        std::cerr << "Ошибка: не удалось создать выходной файл.\n";
        return 1;
    }

    std::copy(arr.begin(), arr.end(), std::ostreambuf_iterator<char>(out));

    return 0;
}