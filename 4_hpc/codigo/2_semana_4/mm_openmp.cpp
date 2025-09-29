#include <omp.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>
#include <iostream>

int main(int argc, char** argv) {
    int N = 4096;
    int threads = 0; // opcional
    if (argc >= 2) N = std::atoi(argv[1]);
    if (argc >= 3) threads = std::atoi(argv[2]);
    if (threads > 0) omp_set_num_threads(threads);

    std::vector<double> A((size_t)N*N), B((size_t)N*N), C((size_t)N*N, 0.0);

    std::mt19937_64 g(42);
    std::uniform_real_distribution<double> d(-1.0,1.0);
    for (size_t i=0;i<(size_t)N*N;++i){ A[i]=d(g); B[i]=d(g); }

    double t0 = omp_get_wtime();

    // Paralelizamos por filas de C (cada hilo tiene una fila exclusiva)
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < N; ++i) {
        const double* Ai = &A[(size_t)i * N];
        double* Ci       = &C[(size_t)i * N];
        for (int k = 0; k < N; ++k) {
            const double aik = Ai[k];
            const double* Bk = &B[(size_t)k * N];   // fila k-ésima de B (contigua)
            // Recorrido contiguo de B y C: se vectoriza bien
            #pragma omp simd
            for (int j = 0; j < N; ++j) {
                Ci[j] += aik * Bk[j];
            }
        }
    }

    double t1 = omp_get_wtime();

    const double secs = t1 - t0;
    const double gflops = (2.0 * (double)N * N * N) / (secs * 1e9);
    int used = omp_get_max_threads(); 

    std::printf("N=%d, threads=%d\n", N, used);
    std::printf("Tiempo GEMM: %.6f s\n", secs);
    std::printf("Rendimiento: %.2f GFLOP/s\n", gflops);
    return 0;
}

