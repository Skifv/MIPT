#include <mpi.h>
#include <iostream>
#include <random>
#include <vector>
#include <iomanip>

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    long long n_total = 1000000000;
    long long n_local = n_total / size;

    if (rank < n_total % size) {
        n_local++; // Первые процессы забирают по одной лишней точке из остатка
    }

    std::mt19937 gen(rank); 
    std::uniform_real_distribution<double> dist(0.0, 1.0);

    long long local_count = 0;

    double start_time = MPI_Wtime();

    for (long long i = 0; i < n_local; ++i) {
        double x = dist(gen);
        double y = dist(gen);
        if (x * x + y * y <= 1.0) {
            local_count++;
        }
    }

    long long total_hits = 0;
    MPI_Reduce(&local_count, &total_hits, 1, MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        double pi = 4.0 * total_hits / n_total;

        double end_time = MPI_Wtime();\

        std::cout << "C++: Pi = " << std::fixed << std::setprecision(10) << pi << ", Time = " << end_time - start_time << "s" << std::endl;
    }

    MPI_Finalize();
    return 0;
}