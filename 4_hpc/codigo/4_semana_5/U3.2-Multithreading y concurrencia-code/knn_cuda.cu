// knn_cuda.cu
// Brute-force kNN en GPU (L2). Cada hilo procesa 1 query y mantiene un top-k en registros.
// Uso didáctico: para N y Q medianos. Para N muy grande, considerar tiling/BLAS/FAISS.
//
// Compilar: nvcc -O3 -arch=sm_80 -std=c++17 knn_cuda.cu -o knn_cuda

#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cmath>
#include <limits>
#include <random>
#include <chrono>
#include <cassert>
#include <cstring>

#include <cuda_runtime.h>
#include <math_constants.h>

#define CUDA_CHECK(ans) { gpuAssert((ans), __FILE__, __LINE__); }
inline void gpuAssert(cudaError_t code, const char *file, int line) {
    if (code != cudaSuccess) {
        fprintf(stderr,"CUDA Error: %s %s %d\n", cudaGetErrorString(code), file, line);
        exit(code);
    }
}

// ------------ insert_topk<K> y kernel knn_kernel<K> ------------
// Usa INFINITY en lugar de CUDART_INF_F (portátil)
template <int K>
__device__ __forceinline__
void insert_topk(float (&best_dist)[K], int (&best_idx)[K], float d, int idx) {
    if (d >= best_dist[0]) return;
    int pos = 0;
    while (pos < K-1 && best_dist[pos+1] > d) {
        best_dist[pos] = best_dist[pos+1];
        best_idx[pos]  = best_idx[pos+1];
        ++pos;
    }
    best_dist[pos] = d;
    best_idx[pos]  = idx;
}

template <int K>
__global__
void knn_kernel(const float* __restrict__ train,
                const float* __restrict__ query,
                int N, int D, int Q,
                int* __restrict__ out_idx,
                float* __restrict__ out_dist2)
{
    int q = blockIdx.x * blockDim.x + threadIdx.x;
    if (q >= Q) return;

    float best_dist[K];
    int   best_idx[K];
    #pragma unroll
    for (int i = 0; i < K; ++i) { best_dist[i] = INFINITY; best_idx[i] = -1; }

    const float* qptr = query + (size_t)q * D;

    for (int n = 0; n < N; ++n) {
        const float* tptr = train + (size_t)n * D;
        float acc = 0.f;
        int d = 0;
        for (; d + 3 < D; d += 4) {
            float a0 = qptr[d]   - tptr[d];
            float a1 = qptr[d+1] - tptr[d+1];
            float a2 = qptr[d+2] - tptr[d+2];
            float a3 = qptr[d+3] - tptr[d+3];
            acc += a0*a0 + a1*a1 + a2*a2 + a3*a3;
        }
        for (; d < D; ++d) {
            float a = qptr[d] - tptr[d];
            acc += a*a;
        }
        insert_topk<K>(best_dist, best_idx, acc, n);
    }

    int base = q * K;
    for (int i = 0; i < K; ++i) {
        int src = K - 1 - i;
        out_idx[base + i]   = best_idx[src];
        out_dist2[base + i] = best_dist[src];
    }
}

struct Args {
    int N=10000, Q=2000, D=64, K=5, seed=123;
};

Args parse(int argc, char** argv){
    Args a;
    for (int i=1;i<argc;i++){
        if (!strcmp(argv[i],"-N") && i+1<argc) a.N=atoi(argv[++i]);
        else if (!strcmp(argv[i],"-Q") && i+1<argc) a.Q=atoi(argv[++i]);
        else if (!strcmp(argv[i],"-D") && i+1<argc) a.D=atoi(argv[++i]);
        else if (!strcmp(argv[i],"-k") && i+1<argc) a.K=atoi(argv[++i]);
        else if (!strcmp(argv[i],"-seed") && i+1<argc) a.seed=atoi(argv[++i]);
        else if (!strcmp(argv[i],"-h")||!strcmp(argv[i],"--help")){
            printf("Uso: %s -N <train> -Q <query> -D <dim> -k <neighbors> -seed <int>\n", argv[0]);
            exit(0);
        }
    }
    return a;
}

int main(int argc, char** argv){
    auto args = parse(argc, argv);
    int N=args.N, Q=args.Q, D=args.D, K=args.K; // N,Q,D pueden sobreescribirse si luego lees de CSV
    assert(K>=1 && K<=32);

    // Info de dispositivo (para SMs, nombre)
    cudaDeviceProp prop{}; CUDA_CHECK(cudaGetDeviceProperties(&prop, 0));
    printf("GPU: %s | SMs=%d | CC=%d.%d\n", prop.name, prop.multiProcessorCount, prop.major, prop.minor);

    printf("KNN mono-GPU | N=%d Q=%d D=%d k=%d\n", N, Q, D, K);

    // Genera datos sintéticos
    std::mt19937 rng(args.seed);
    std::uniform_real_distribution<float> dist(0.0f,1.0f);
    std::vector<float> h_train((size_t)N*D), h_query((size_t)Q*D);
    for (auto &x : h_train) x = dist(rng);
    for (auto &x : h_query) x = dist(rng);

    // Reserva GPU
    float *d_train=nullptr, *d_query=nullptr;
    int   *d_idx=nullptr; float *d_dist2=nullptr;
    CUDA_CHECK(cudaMalloc(&d_train,  sizeof(float)* (size_t)N*D));
    CUDA_CHECK(cudaMalloc(&d_query,  sizeof(float)* (size_t)Q*D));
    CUDA_CHECK(cudaMalloc(&d_idx,    sizeof(int)   * (size_t)Q*K));
    CUDA_CHECK(cudaMalloc(&d_dist2,  sizeof(float) * (size_t)Q*K));

    // Copias H2D
    CUDA_CHECK(cudaMemcpy(d_train, h_train.data(), sizeof(float)*(size_t)N*D, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_query, h_query.data(), sizeof(float)*(size_t)Q*D, cudaMemcpyHostToDevice));

    // Kernel config
    dim3 block(128);
    dim3 grid((Q + block.x - 1) / block.x);

    // Tiempos (solo kernel)
    cudaEvent_t evStart, evStop;
    CUDA_CHECK(cudaEventCreate(&evStart));
    CUDA_CHECK(cudaEventCreate(&evStop));
    CUDA_CHECK(cudaEventRecord(evStart));

    switch (K) {
        case 1:  knn_kernel<1><<<grid,block>>>(d_train,d_query,N,D,Q,d_idx,d_dist2); break;
        case 5:  knn_kernel<5><<<grid,block>>>(d_train,d_query,N,D,Q,d_idx,d_dist2); break;
        case 10: knn_kernel<10><<<grid,block>>>(d_train,d_query,N,D,Q,d_idx,d_dist2); break;
        case 16: knn_kernel<16><<<grid,block>>>(d_train,d_query,N,D,Q,d_idx,d_dist2); break;
        case 32: knn_kernel<32><<<grid,block>>>(d_train,d_query,N,D,Q,d_idx,d_dist2); break;
        default: knn_kernel<16><<<grid,block>>>(d_train,d_query,N,D,Q,d_idx,d_dist2); break;
    }
    CUDA_CHECK(cudaPeekAtLastError());
    CUDA_CHECK(cudaDeviceSynchronize());

    CUDA_CHECK(cudaEventRecord(evStop));
    CUDA_CHECK(cudaEventSynchronize(evStop));
    float ms_kernel=0.f; CUDA_CHECK(cudaEventElapsedTime(&ms_kernel, evStart, evStop));

    // Copia resultados
    std::vector<int>   h_idx((size_t)Q*K);
    std::vector<float> h_dist2((size_t)Q*K);
    CUDA_CHECK(cudaMemcpy(h_idx.data(), d_idx, sizeof(int)*(size_t)Q*K, cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_dist2.data(), d_dist2, sizeof(float)*(size_t)Q*K, cudaMemcpyDeviceToHost));

    // (Mostrar primeras queries si quieres)
    for (int q=0; q < std::min(Q,3); ++q){
        printf("Q[%d]: ", q);
        for (int i=0;i<K;++i){
            printf("(%d, %.4f) ", h_idx[q*K+i], h_dist2[q*K+i]);
        }
        printf("\n");
    }

    // ======================
    // Métricas de performance
    // ======================
    const double t_s = ms_kernel / 1e3;                  // segundos
    const long long pairs = (long long)N * (long long)Q; // comparaciones
    // FLOPs: por dimensión hacemos: 1 resta, 1 multiplicación, 1 suma  => 3 FLOPs
    const double flops = (double)pairs * (double)D * 3.0;
    // Bytes leídos/escritos (modelo ingenuo)
    const double bytes_read  = (double)pairs * (double)D * 2.0 * sizeof(float); // train + query
    const double bytes_write = (double)Q * (double)K * (sizeof(int) + sizeof(float));
    const double bytes_total = bytes_read + bytes_write;

    const double gflops   = flops / 1e9;
    const double gbs      = bytes_total / 1e9;
    const double gflops_s = gflops / t_s;
    const double gbs_s    = gbs    / t_s;

    const long long total_threads = (long long)grid.x * (long long)block.x;
    const double ms_per_query = ms_kernel / (double)Q;
    const double queries_per_s = (double)Q / t_s;

    printf("\n=== Métricas GPU ===\n");
    printf("Grid.x=%d | Block.x=%d | Hilos totales lanzados=%lld\n", grid.x, block.x, total_threads);
    printf("Kernel time: %.3f ms\n", ms_kernel);
    printf("Comparaciones (pairs = N*Q): %lld\n", pairs);
    printf("FLOPs (3*D por par): %.3f GFLOPs | Throughput: %.3f GFLOP/s\n", gflops, gflops_s);
    printf("Bytes (naive): leidos ~ %.3f GB, escritos ~ %.6f GB, total ~ %.3f GB | Throughput: %.3f GB/s\n",
           bytes_read/1e9, bytes_write/1e9, bytes_total/1e9, gbs_s);
    printf("ms/query: %.6f | queries/s: %.2f\n", ms_per_query, queries_per_s);
    printf("SMs GPU: %d\n", prop.multiProcessorCount);

    // Limpieza
    cudaFree(d_train); cudaFree(d_query);
    cudaFree(d_idx);   cudaFree(d_dist2);
    cudaEventDestroy(evStart); cudaEventDestroy(evStop);
    return 0;
}

