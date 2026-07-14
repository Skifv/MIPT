#include <iostream>
#include <unistd.h>
#include <sys/wait.h>
#include <chrono>

const int ITERS = 100000;

int main() {
    int p2c[2], c2p[2];
    // Создаем два пайпа: parent-to-child и child-to-parent
    if (pipe(p2c) != 0 || pipe(c2p) != 0) return 1;

    pid_t pid = fork();
    if (pid == 0) { // --- ДОЧЕРНИЙ ПРОЦЕСС ---
        close(p2c[1]); close(c2p[0]); // Закрываем неиспользуемые концы
        
        int val;
        for (int i = 0; i < ITERS; ++i) {
            read(p2c[0], &val, sizeof(val));  // Ждем от родителя
            write(c2p[1], &val, sizeof(val)); // Отправляем обратно
        }
        close(p2c[0]); close(c2p[1]);
        return 0;
    }

    // --- РОДИТЕЛЬСКИЙ ПРОЦЕСС ---
    close(p2c[0]); close(c2p[1]); 
    
    int val = 1;
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < ITERS; ++i) {
        write(p2c[1], &val, sizeof(val)); // Пинг
        read(c2p[0], &val, sizeof(val));  // Понг
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    wait(NULL); // Ждем завершения дочернего процесса
    
    close(p2c[1]); close(c2p[0]);

    std::chrono::duration<double> diff = end - start;
    std::cout << "Pipe 1-way latency: " 
              << (diff.count() / (2.0 * ITERS)) * 1e6 << " us\n";
              
    return 0;
}