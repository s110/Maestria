#include <iostream>
#include <vector>
#include <chrono>
#include <omp.h>

void matrix_multiply(const double* A, const double* B, double* C, int N) {
    #pragma omp parallel for
    for (int i = 0; i < N; ++i) {
        for (int k = 0; k < N; ++k) {
            double a_ik = A[i * N + k];
            for (int j = 0; j < N; ++j) {
                C[i * N + j] += a_ik * B[k * N + j]; // 1 mul + 1 add
            }
        }
    }
}

int main() {
    const int N = 4096;
    const int FLOP_PER_ITER = 2;
    omp_set_num_threads(8);
    // Asignar matrices A, B y C en una sola dimensión (planas)
    std::vector<double> A(N * N, 1.0);
    std::vector<double> B(N * N, 1.0);
    std::vector<double> C(N * N, 0.0);

    auto start = std::chrono::high_resolution_clock::now();

    matrix_multiply(A.data(), B.data(), C.data(), N);

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    double seconds = elapsed.count();
    double total_flops = static_cast<double>(N) * N * N * FLOP_PER_ITER;
    double gflops = total_flops / 1e9 / seconds;

    std::cout << "Tiempo: " << seconds << " segundos\n";
    std::cout << "Rendimiento: " << gflops << " GFLOPs\n";
    std::cout << "Ejemplo: C[0] = " << C[0] << "\n";

    return 0;
}

