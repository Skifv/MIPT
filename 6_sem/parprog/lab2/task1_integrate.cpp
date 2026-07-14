#include <iostream>
#include <cmath>
#include <string>
#include "integrator.h"

double target_func(double x) {
    return std::sin(1.0 / x);
}

int main(int argc, char* argv[]) {
    // Ждем ровно 6 параметров (+1 имя программы)
    if (argc < 7) {
        std::cerr << "Использование: " << argv[0] << " <threads> <a> <b> <eps> <N> <max_depth>\n";
        std::cerr << "Например: " << argv[0] << " 4 0.01 1.0 1e-6 20 30\n";
        return 1;
    }
    
    int num_threads = std::stoi(argv[1]);
    double a = std::stod(argv[2]);
    double b = std::stod(argv[3]);
    double eps = std::stod(argv[4]);
    int N = std::stoi(argv[5]);
    int max_depth = std::stoi(argv[6]);

    try {
        IntegrationResult res = integrate(a, b, target_func, eps, num_threads, N, max_depth);
        std::cout << "Integral: " << res.integral << "\n";
        std::cout << "Error: " << res.estimated_error << "\n";
        std::cout << "Time: " << res.time_sec << "\n";
    } catch(const std::exception& e) {
        std::cerr << "Ошибка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}