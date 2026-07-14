#ifndef INTEGRATOR_H
#define INTEGRATOR_H

#include <vector>

struct IntegrationResult {
    double integral;
    double time_sec;
    double estimated_error; // Оценка реально достигнутой погрешности
};

// Функция многопоточного адаптивного интегрирования (метод Симпсона)
IntegrationResult integrate(double a, double b, double (*f)(double), 
                            double eps, int num_threads, int N, int max_depth);

#endif // INTEGRATOR_H