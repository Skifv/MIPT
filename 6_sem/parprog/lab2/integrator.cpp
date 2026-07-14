#include "integrator.h"
#include <cmath>
#include <queue>
#include <memory>
#include <stdexcept>
#include <pthread.h>
#include <chrono>

// Описание одного отрезка интегрирования, отправляемого в пул потоков
struct Task {
    double a;
    double b;
    double I_full;              // Интеграл для данного отрезка, посчитанный на предыдущем шаге (для оценки погрешности)
    double eps;                 // Допустимая погрешность конкретно для этого отрезка
    std::vector<double> f_vals; // Значения функции в узлах (N+1 штук). Позволяет не пересчитывать их при дроблении.
    int depth;                  // Текущая глубина рекурсии (защита от зацикливания)
};

// Общий контекст для всех потоков
struct ThreadPoolContext {
    std::queue<Task> task_queue;
    pthread_mutex_t mutex;
    pthread_cond_t cv;
    pthread_cond_t cv_done;
    
    int active_tasks;
    bool stop;
    
    double total_integral;      // Глобальный аккумулятор результата
    double total_error;         // Накопленная суммарная ошибка
    
    double (*func)(double);
    int N;
    int max_depth;
};

// Вычисление интеграла по формуле Симпсона (требует четного N)
double calc_integral_simp(const std::vector<double>& fv, double h) {
    double sum = fv.front() + fv.back();
    for (size_t i = 1; i < fv.size() - 1; ++i) {
        sum += (i % 2 != 0 ? 4.0 : 2.0) * fv[i];
    }
    return sum * (h / 3.0);
}

void* worker_routine(void* arg) {
    auto ctx = static_cast<ThreadPoolContext*>(arg);
    int N = ctx->N;
    
    // Для метода Симпсона (4-й порядок точности) знаменатель в правиле Рунге равен 2^4 - 1 = 15
    const double RUNGE_DENOM = 15.0; 
    
    while (true) {
        pthread_mutex_lock(&ctx->mutex);
        
        // Поток засыпает, если нет задач и нет сигнала остановки
        while (ctx->task_queue.empty() && !ctx->stop) {
            pthread_cond_wait(&ctx->cv, &ctx->mutex);
        }
        
        if (ctx->stop && ctx->task_queue.empty()) {
            pthread_mutex_unlock(&ctx->mutex);
            break;
        }
        
        Task task = std::move(ctx->task_queue.front());  // Чтобы не копировать вектор в Task
        ctx->task_queue.pop();
        ctx->active_tasks++;
        pthread_mutex_unlock(&ctx->mutex);
        
        double m = task.a + (task.b - task.a) / 2.0;
        double h_new = (task.b - task.a) / (2.0 * N);
        
        std::vector<double> f_L(N + 1);
        std::vector<double> f_R(N + 1);
        
        // Вычисляем новые точки. Четные узлы совпадают со старыми — берем из памяти (f_vals)
        for (int i = 0; i <= N; ++i) {
            f_L[i] = (i % 2 == 0) ? task.f_vals[i / 2] : ctx->func(task.a + i * h_new);
            f_R[i] = (i % 2 == 0) ? task.f_vals[N / 2 + i / 2] : ctx->func(m + i * h_new);
        }
        
        double I_L = calc_integral_simp(f_L, h_new);
        double I_R = calc_integral_simp(f_R, h_new);
        
        // Оценка погрешности по Рунге (delta сохраняет знак для экстраполяции)
        double delta = (I_L + I_R - task.I_full) / RUNGE_DENOM;
        double current_error_abs = std::abs(delta);
        
        bool converged = current_error_abs < task.eps;
        
        // Защита от бесконечного деления (особенность функции или достижение предела типа double, когда a == m)
        bool forced_stop = (task.depth >= ctx->max_depth) || (m <= task.a || m >= task.b);
        
        pthread_mutex_lock(&ctx->mutex);
        if (converged || forced_stop) {
            // Экстраполяция Ричардсона (+ delta) уточняет значение до 6-го порядка
            ctx->total_integral += (I_L + I_R) + delta;
            ctx->total_error += current_error_abs; // Накапливаем реальную погрешность
        } else {
            // Требование к eps дробится на 2, чтобы суммарная ошибка на отрезке [a,b] не превысила исходную
            ctx->task_queue.push({task.a, m, I_L, task.eps / 2.0, std::move(f_L), task.depth + 1});
            ctx->task_queue.push({m, task.b, I_R, task.eps / 2.0, std::move(f_R), task.depth + 1});
            pthread_cond_broadcast(&ctx->cv); // Будим простаивающие потоки для новых задач
        }
        
        ctx->active_tasks--;
        // Сигнал главному потоку, что вся работа окончена
        if (ctx->active_tasks == 0 && ctx->task_queue.empty()) {
            pthread_cond_signal(&ctx->cv_done);
        }
        pthread_mutex_unlock(&ctx->mutex);
    }
    
    return nullptr;
}

IntegrationResult integrate(double a, double b, double (*f)(double), 
                            double eps, int num_threads, int N, int max_depth) {
    if (N % 2 != 0 || N <= 0) {
        throw std::invalid_argument("N должно быть положительным четным числом");
    }
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    auto ctx = std::make_unique<ThreadPoolContext>();
    pthread_mutex_init(&ctx->mutex, nullptr);
    pthread_cond_init(&ctx->cv, nullptr);
    pthread_cond_init(&ctx->cv_done, nullptr);
    
    ctx->active_tasks = 0;
    ctx->stop = false;
    ctx->total_integral = 0.0;
    ctx->total_error = 0.0;
    ctx->func = f;
    ctx->N = N;
    ctx->max_depth = max_depth;
    
    // Формирование первичной задачи (весь отрезок [a, b])
    double h = (b - a) / N;
    std::vector<double> f_vals(N + 1);
    for (int i = 0; i <= N; ++i) {
        f_vals[i] = f(a + i * h);
    }
    double I_full = calc_integral_simp(f_vals, h);
    
    ctx->task_queue.push({a, b, I_full, eps, std::move(f_vals), 0});
    
    // Запуск потоков
    auto threads = std::make_unique<pthread_t[]>(num_threads);
    for (int i = 0; i < num_threads; ++i) {
        pthread_create(&threads[i], nullptr, worker_routine, ctx.get());
    }
    
    // Ожидание полной остановки вычислений
    pthread_mutex_lock(&ctx->mutex);
    while (ctx->active_tasks > 0 || !ctx->task_queue.empty()) {
        pthread_cond_wait(&ctx->cv_done, &ctx->mutex);
    }
    ctx->stop = true;
    pthread_cond_broadcast(&ctx->cv);
    pthread_mutex_unlock(&ctx->mutex);
    
    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], nullptr);
    }
    
    pthread_mutex_destroy(&ctx->mutex);
    pthread_cond_destroy(&ctx->cv);
    pthread_cond_destroy(&ctx->cv_done);
    
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end_time - start_time;
    
    return {ctx->total_integral, diff.count(), ctx->total_error};
}