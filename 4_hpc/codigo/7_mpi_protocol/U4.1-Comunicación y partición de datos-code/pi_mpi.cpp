/*************************************************
 * Este archivo fue escrito como ejemplo en el curso HPC Aplicada,
 * de la Universidad de Ingeniería y Tecnología (UTEC)
 * Material es de libre uso, entendiendo que debe contener este encabezado
 * UTEC no se responsabiliza del uso particular del código
 *
 * Autor:       Jose Fiestas (UTEC)
 * contacto:    jfiestas@utec.edu.pe
 * objetivo:    Calculo de PI en un sistema distribuido
 * contenido:   código fuente en C+ pi_mpi.cpp
  *************************************************/
#include <mpi.h>
#include <cmath>
#include <iostream>
#include <iomanip>
#include <cstdlib>
#include <cstdint>

inline double f(double x) {
    return 4.0 / (1.0 + x * x);
}

// Divide [0, n_items) en 'size' bloques casi iguales; retorna (i0, i1) con i1 exclusivo
static inline void chunk_bounds(uint64_t n_items, int rank, int size, uint64_t& i0, uint64_t& i1) {
    uint64_t base = n_items / static_cast<uint64_t>(size);
    uint64_t rem  = n_items % static_cast<uint64_t>(size);
    i0 = rank * base + static_cast<uint64_t>(std::min<int>(rank, static_cast<int>(rem)));
    i1 = i0 + base + (rank < static_cast<int>(rem) ? 1ULL : 0ULL);
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank = 0, size = 1;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Parámetros: nsteps desde línea de comando
    uint64_t nsteps = 1ULL << 20; // 1,048,576
    if (argc >= 2) {
        char* endptr = nullptr;
        unsigned long long v = std::strtoull(argv[1], &endptr, 10);
        if (endptr != argv[1] && *endptr == '\0' && v > 0ULL) nsteps = static_cast<uint64_t>(v);
        if (rank == 0 && (endptr == argv[1] || *endptr != '\0' || v == 0ULL)) {
            std::cerr << "Advertencia: argumento inválido para nsteps; usando valor por defecto " << nsteps << "\n";
        }
    }

    const double a = 0.0, b = 1.0;
    const double dx = (b - a) / static_cast<double>(nsteps);

    // Medición de tiempo
    MPI_Barrier(MPI_COMM_WORLD);
    const double t0 = MPI_Wtime();
    
    // Rango local del proceso
    uint64_t i0 = 0, i1 = 0;
    chunk_bounds(nsteps, rank, size, i0, i1);

    // Cálculo local (regla del punto medio)
    double local_sum = 0.0;
    for (uint64_t i = i0; i < i1; ++i) {
        const double xmid = a + (static_cast<double>(i) + 0.5) * dx;
        local_sum += f(xmid);
    }
    const double local_val = local_sum * dx;

    double pi_est = 0.0;

    // Reducción: suma en el root (rank 0)
    MPI_Reduce(&local_val, &pi_est, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    MPI_Barrier(MPI_COMM_WORLD);
    const double t1 = MPI_Wtime();

    if (rank == 0) {
        const double err = std::abs(M_PI - pi_est);
        std::cout << std::fixed << std::setprecision(12);
        std::cout << "Reduce | metodo=midpoint  nsteps=" << nsteps
                  << "  procs=" << size
                  << "  tiempo=" << (t1 - t0) << "s\n";
        std::cout << "pi " << pi_est << "  | error=" << std::scientific << err << "\n";
    }

    MPI_Finalize();
    return 0;
}

