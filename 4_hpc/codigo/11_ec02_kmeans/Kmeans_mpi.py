#!/usr/bin/env python3
"""
K-means 2D con NumPy + mpi4py (distribuido por datos).
"""

import time
import numpy as np
import os
from mpi4py import MPI
# import matplotlib
# matplotlib.use("Agg")  # para que funcione sin entorno gráfico
# import matplotlib.pyplot as plt

# Colores para graficar (si activas matplotlib)
#COLORS = ['red', 'green', 'blue', 'orange', 'purple', 'brown', 'pink', 'gray']

# ------------------------------------------------------------
# Generación de datos
# ------------------------------------------------------------
def generate_2d_clusters(n_clusters, points_per_cluster, spread=1.5, seed=42):
    """
    Genera datos sintéticos 2D agrupados en 'n_clusters'.
    Cada cluster tiene 'points_per_cluster' puntos.
    """
    rng = np.random.default_rng(seed)
    centers = rng.uniform(-10, 10, size=(n_clusters, 2))  # centros verdaderos

    data = []
    for cx, cy in centers:
        # puntos alrededor de cada centro con distribución normal
        cluster_points = rng.normal(
            loc=(cx, cy),
            scale=spread,
            size=(points_per_cluster, 2)
        )
        data.append(cluster_points)

    data = np.vstack(data)  # (n_clusters * points_per_cluster, 2)
    return data


def init_centers_global(points, k, rng):
    """
    Elige k centros iniciales al azar desde el conjunto completo (en root).
    """
    n_points = points.shape[0]
    idx = rng.choice(n_points, size=k, replace=False)
    return points[idx, :]


# ------------------------------------------------------------
# K-means paralelo
# ------------------------------------------------------------
def kmeans_parallel(comm, local_points, k, tol=1e-3, max_iters=100, verbose=False):
    """
    K-means paralelo (por datos) usando MPI y NumPy.

    - comm: comunicador MPI.
    - local_points: subconjunto de puntos que posee cada proceso (shape: [n_local, 2]).
    - k: número de clusters.
    - tol: tolerancia para convergencia (norma L2 del cambio en centros).
    - max_iters: máximo de iteraciones.
    """
    rank = comm.Get_rank()
    dim = local_points.shape[1]

    # --- Inicialización de centro ---
    all_points_list = comm.gather(local_points, root=0)

    if rank == 0:
        rng = np.random.default_rng(123)
        all_points = np.vstack(all_points_list)
        centers = init_centers_global(all_points, k, rng)
    else:
        centers = None

    # Broadcast de centros iniciales a todos
    centers = comm.bcast(centers, root=0)

    if verbose and rank == 0:
        print(f"[Iter 0] Initial centers:\n{centers}")

    # --- Bucle principal de K-means ---
    for it in range(1, max_iters + 1):
        # Etapa 1: asignación local
        diffs = local_points[:, np.newaxis, :] - centers[np.newaxis, :, :]
        dist_sq = np.sum(diffs ** 2, axis=2)  # [n_local, k]
        labels = np.argmin(dist_sq, axis=1)   # [n_local]

        # Etapa 2: acumulación local
        local_sum = np.zeros((k, dim), dtype=np.float64)
        local_count = np.zeros(k, dtype=np.int64)

        for j in range(k):
            mask = (labels == j)
            if np.any(mask):
                local_sum[j] = np.sum(local_points[mask], axis=0)
                local_count[j] = np.count_nonzero(mask)

        # Reducción global
        global_sum = np.zeros_like(local_sum)
        global_count = np.zeros_like(local_count)

        comm.Allreduce(local_sum, global_sum, op=MPI.SUM)
        comm.Allreduce(local_count, global_count, op=MPI.SUM)

        # Cálculo de nuevos centros
        new_centers = np.copy(centers)
        for j in range(k):
            if global_count[j] > 0:
                new_centers[j] = global_sum[j] / global_count[j]
            # Si global_count[j] == 0, mantenemos el centro anterior

        # Chequeo de convergencia
        shift = np.linalg.norm(new_centers - centers)
        centers = new_centers

        if verbose and rank == 0:
            print(f"[Iter {it}] shift = {shift:.6f}")

        centers = comm.bcast(centers, root=0)

        if shift < tol:
            if rank == 0 and verbose:
                print(f"Converged at iteration {it} with shift={shift:.6e}")
            break

    return centers, labels


# ------------------------------------------------------------
# Programa principal
# ------------------------------------------------------------
def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Parámetros globales
    k = 3                      # número de clusters
    dim = 2
    tol = 1e-3
    max_iters = 100
    verbose = (rank == 0)

    # Leer N desde variable de entorno (para SLURM)
    N_env = os.environ.get("KMEANS_N")
    if N_env is None:
        N = 12000  # valor por defecto si no se envía nada
    else:
        N = int(N_env)

    # Repartimos N en k clusters más o menos iguales
    points_per_cluster = max(1, N // k)

    if rank == 0:
        print(f"[INFO] N total pedido = {N}, points_per_cluster = {points_per_cluster}")

    # --- Generación de datos (solo en root) ---
    if rank == 0:
        full_data = generate_2d_clusters(
            n_clusters=k,
            points_per_cluster=points_per_cluster,
            spread=1.5,
            seed=42
        )
        n_total = full_data.shape[0]

        # Reparto manual: counts + displs (más robusto que array_split)
        counts = [(n_total // size) + (1 if r < n_total % size else 0)
                  for r in range(size)]
        displs = [sum(counts[:r]) for r in range(size)]
        chunks = [full_data[displs[r]:displs[r] + counts[r], :]
                  for r in range(size)]

        print(f"[ROOT] N_total generado = {n_total}, size = {size}")
        for r in range(size):
            print(f"  Rank {r} recibirá {counts[r]} puntos")
    else:
        chunks = None
        n_total = None


    t0 = time.time()
    # Broadcast de N_total (solo informativo)
    n_total = comm.bcast(n_total, root=0)

    # Scatter de los datos a todos los procesos
    local_points = comm.scatter(chunks, root=0)
    local_n = local_points.shape[0]

    t1 = time.time()
    if rank == 0:
        print(f"Total points: {n_total}, MPI size: {size}")
    print(f"Rank {rank} has {local_n} points.")

    # --- Ejecutar K-means paralelo ---
    #comm.Barrier()
    t2 = time.time()

    centers, local_labels = kmeans_parallel(
        comm=comm,
        local_points=local_points,
        k=k,
        tol=tol,
        max_iters=max_iters,
        verbose=verbose
    )

   # comm.Barrier()
    t3 = time.time()

    if rank == 0:
        print(f"K-means Tcomp {t3 - t2:.6f} seconds.")
        print(f"K-means Tcomm {t1 - t0:.6f} seconds.")
        print("Final centers:")
        print(centers)

    # --- Reunir resultados para posible graficado (solo root) ---
   # all_points_list = comm.gather(local_points, root=0)
   # all_labels_list = comm.gather(local_labels, root=0)

#    if rank == 0:
 #       all_points = np.vstack(all_points_list)
  #      all_labels = np.concatenate(all_labels_list)

        # Si quieres activar el plot, descomenta esta sección
        """
        plt.figure(figsize=(6, 6))
        for j in range(k):
            mask = (all_labels == j)
            if np.any(mask):
                xs = all_points[mask, 0]
                ys = all_points[mask, 1]
                color = COLORS[j % len(COLORS)]
                plt.scatter(xs, ys, s=10, alpha=0.7, c=color, label=f"Cluster {j}")

        plt.scatter(centers[:, 0], centers[:, 1],
                    c='black', marker='x', s=120, linewidths=3, label='Centers')

        plt.title(f"K-means 2D con NumPy + MPI (N={n_total}, p={size})")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("kmeans_mpi_numpy_2d.png")
        print("Plot saved as kmeans_mpi_numpy_2d.png")
        """


if __name__ == "__main__":
    main()

