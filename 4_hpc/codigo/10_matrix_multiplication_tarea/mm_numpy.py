import numpy as np
from joblib import Parallel, delayed
import time

N = 4096  # Tamaño reducido para evitar saturar CPU

A = np.ones((N, N))
B = np.ones((N, N))
C = np.zeros((N, N))

def compute_row(i):
    return np.dot(A[i, :], B)

start = time.time()

# Computa cada fila de la matriz C en paralelo
C_rows = Parallel(n_jobs=1)(delayed(compute_row)(i) for i in range(N))
C = np.vstack(C_rows)

end = time.time()
elapsed = end - start
gflops = (2 * N**3) / 1e9 / elapsed

print(f"Tiempo: {elapsed:.4f} segundos")
print(f"Rendimiento: {gflops:.2f} GFLOPs")
print(f"C[0,0] = {C[0,0]}")

