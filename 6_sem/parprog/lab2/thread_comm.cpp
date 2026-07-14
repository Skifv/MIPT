#include <iostream>
#include <pthread.h>
#include <chrono>

const int ITERS = 100000;

pthread_mutex_t mtx = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cv = PTHREAD_COND_INITIALIZER;

// Флаг очереди: false - очередь main, true - очередь worker
bool turn = false; 

void* worker_thread(void* arg) {
    for (int i = 0; i < ITERS; ++i) {
        pthread_mutex_lock(&mtx); 
        
        // Пока очередь не наша (turn == false), спим
        while (!turn) { 
            pthread_cond_wait(&cv, &mtx);
        }
        
        turn = false; // Меняем флаг (Понг)
        
        pthread_cond_signal(&cv); // Будим главный поток
        pthread_mutex_unlock(&mtx); // Снимаем замок
    }
    return nullptr;
}

int main() {
    pthread_t worker;
    pthread_create(&worker, nullptr, worker_thread, nullptr);

    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < ITERS; ++i) {
        pthread_mutex_lock(&mtx);
        
        turn = true; // Передаем ход (Пинг)
        pthread_cond_signal(&cv); // Будим рабочий поток
        
        // Ждем, пока рабочий поток вернет ход обратно (пока turn не станет false)
        while (turn) { 
            pthread_cond_wait(&cv, &mtx);
        }
        
        pthread_mutex_unlock(&mtx);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    
    // Дожидаемся завершения потока
    pthread_join(worker, nullptr);

    std::chrono::duration<double> diff = end - start;
    std::cout << "Threads 1-way latency: " 
              << (diff.count() / (2.0 * ITERS)) * 1e6 << " us\n";
              
    return 0;
}