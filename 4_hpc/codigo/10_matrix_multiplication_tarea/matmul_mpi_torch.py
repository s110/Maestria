import argparse
import time

import numpy as np
import torch
from mpi4py import MPI


def main():
    # --- 1. Inicialización de MPI ---
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # --- 2. Parseo de Argumentos (solo en el proceso raíz) ---
    total_wall_clock_start = 0
    if rank == 0:
        total_wall_clock_start = time.time()
        parser = argparse.ArgumentParser(
            description="Matrix multiplication with mpi4py and PyTorch."
        )
        parser.add_argument(
            "--size", type=int, required=True, help="Size N for the NxN matrices."
        )
        parser.add_argument(
            "--verify",
            action="store_true",
            help="Verify the result against sequential computation.",
        )
        args = parser.parse_args()
        matrix_size = args.size
        verify = args.verify

        # Validación: El tamaño de la matriz debe ser divisible por el número de procesos
        if matrix_size % size != 0:
            print(
                f"Error: El tamaño de la matriz ({matrix_size}) debe ser divisible por el número de procesos ({size})."
            )
            comm.Abort(1)  # Termina todos los procesos MPI
    else:
        # Los otros procesos reciben los parámetros vía Bcast
        matrix_size = None
        verify = None

    # --- 3. Distribución de Parámetros de Configuración ---
    # El raíz transmite el tamaño de la matriz a todos los procesos
    matrix_size = comm.bcast(matrix_size, root=0)
    verify = comm.bcast(verify, root=0)

    # Determinar el dispositivo (CPU o GPU si está disponible)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # --- 4. Creación y Distribución de Datos (orquestado por el raíz) ---
    A = None
    B = None
    A_sub = None

    # El proceso raíz crea las matrices
    if rank == 0:
        print(
            f"Iniciando cálculo en {size} procesos para matrices de {matrix_size}x{matrix_size} en dispositivo '{device}'."
        )
        # Usamos torch.float32 para cálculos eficientes
        A = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32)
        B = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32)

        # Scatter se encargará de dividir la matriz A.
    else:
        pass

    # Todos los procesos preparan un buffer para recibir su parte de A
    # Cada proceso recibirá N/size filas
    rows_per_process = matrix_size // size
    A_sub = torch.empty(
        rows_per_process, matrix_size, device=device, dtype=torch.float32
    )

    # B necesita ser un tensor vacío en los procesos no-raíz antes del Bcast
    if rank != 0:
        B = torch.empty(matrix_size, matrix_size, device=device, dtype=torch.float32)

    # Sincronizar todos los procesos antes de medir el tiempo
    comm.Barrier()

    # --- 5. Medición de Tiempos ---

    kernel_start_time = time.time()

    # --- TIEMPO DE COMUNICACIÓN (Distribución) ---
    comm_start_time = time.time()

    # Bcast: Enviar la matriz B completa a todos los procesos
    comm.Bcast([B, MPI.FLOAT], root=0)

    # Scatter: Repartir las franjas de A a cada proceso.
    # La versión en mayúsculas (Scatter) requiere un buffer contiguo (la matriz A completa)
    # en el proceso raíz y se encarga de la división.
    comm.Scatter(
        [A, MPI.FLOAT] if rank == 0 else [None, MPI.FLOAT],
        [A_sub, MPI.FLOAT],
        root=0,
    )

    comm_distribute_time = time.time() - comm_start_time

    # --- TIEMPO DE CÓMPUTO ---
    comp_start_time = time.time()

    # Cada proceso realiza su multiplicación local
    C_sub = torch.matmul(A_sub, B)

    comp_time = time.time() - comp_start_time

    # --- TIEMPO DE COMUNICACIÓN (Recolección) ---
    comm_start_time = time.time()

    # Buffer para recibir los resultados en el proceso raíz
    C_result = None
    if rank == 0:
        # Preparamos un único tensor para recibir los datos de todos los procesos
        C_result = torch.empty(
            matrix_size, matrix_size, device=device, dtype=torch.float32
        )

    # Gather: Recolectar los resultados parciales en el proceso raíz
    # La versión en mayúsculas (Gather) requiere un buffer contiguo en el proceso raíz.
    comm.Gather(
        [C_sub, MPI.FLOAT],
        [C_result, MPI.FLOAT] if rank == 0 else [None, MPI.FLOAT],
        root=0,
    )

    comm_gather_time = time.time() - comm_start_time

    kernel_time = time.time() - kernel_start_time

    # Recolectamos los tiempos de cómputo de todos los procesos.
    # Esta es una operación colectiva, todos los procesos deben llamarla.
    all_comp_times = comm.gather(comp_time, root=0)

    # --- 6. Reporte de Resultados (solo en el proceso raíz) ---
    if rank == 0:
        total_wall_clock_time = time.time() - total_wall_clock_start
        # El resultado ya está completo en C_result, no es necesario concatenar.

        # Calcular tiempos totales
        total_comm_time = comm_distribute_time + comm_gather_time

        # Para el tiempo de cómputo, tomamos el máximo entre todos los procesos,
        # ya que el tiempo total está limitado por el proceso más lento.
        max_comp_time = max(all_comp_times)

        print("--- Resultados del Rendimiento ---")
        print(f"Procesos MPI:            {size}")
        print(f"Tamaño de Matriz:        {matrix_size}x{matrix_size}")
        print(f"Tiempo Total (Wall-Clock): {total_wall_clock_time:.6f} s")
        print(f"Tiempo Total (Kernel Paralelo): {kernel_time:.6f} s")
        print(f"Tiempo de Comunicación:  {total_comm_time:.6f} s")
        print(f"Tiempo de Cómputo (max): {max_comp_time:.6f} s")

        # Verificación opcional
        if verify:
            print("\n--- Verificación ---")
            start_verify = time.time()
            C_sequential = torch.matmul(A, B)
            end_verify = time.time()
            print(f"Tiempo de cómputo secuencial: {end_verify - start_verify:.6f} s")
            if torch.allclose(C_result, C_sequential, atol=1e-5):
                print("Resultado VERIFICADO: La multiplicación paralela es correcta.")
            else:
                print("Error de VERIFICACIÓN: El resultado es incorrecto.")


if __name__ == "__main__":
    main()  # Ejecución: mpiexec -n <num_procesos> python matmul_mpi_torch.py --size <N>
