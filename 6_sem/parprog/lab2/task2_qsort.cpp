#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <cstdlib>
#include <chrono>
#include <iterator>
#include <cstring>

int cmp_double(const void* a, const void* b) {
    double da = *(const double*)a;
    double db = *(const double*)b;
    return (da > db) - (da < db);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Использование: " << argv[0] << " <input.bin>\n";
        return 1;
    }

    std::string input_file = argv[1];

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

    // Замер времени std::qsort
    auto start_q = std::chrono::high_resolution_clock::now();
    std::qsort(arr.data(), num_elements, sizeof(double), cmp_double);
    auto end_q = std::chrono::high_resolution_clock::now();
    
    std::chrono::duration<double> diff_q = end_q - start_q;
    std::cout << "QSort Time: " << diff_q.count() << "\n";

    return 0;
}