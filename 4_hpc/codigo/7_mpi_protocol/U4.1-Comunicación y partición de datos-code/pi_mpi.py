"""-----------------------------------------------
Este archivo fue escrito como ejemplo en el curso HPC Aplicada
de la Universidad de Ingeniería y Tenología (UTEC)
Material es de libre uso, entendiendo que debe contener este encabezado
UTEC no se responsabiliza del uso particular del código

Autor:      Jose Fiestas (UTEC)
contacto:   jfiestas@utec.edu.pe
objetivo:   Calculo de PI en un sistema distribuido, en Python
contenido:  código fuente en Pytho pi_mpi.py
----------------------------------------------- """

from mpi4py import MPI
import math

def f(x):
    return 4.0 / (1.0 + x*x)

def chunk_bounds(n_items, rank, size):
    """Divide [0, n_items) en 'size' bloques casi iguales. Retorna (i0, i1) con i1 exclusivo."""
    base = n_items // size
    rem  = n_items % size
    i0 = rank * base + min(rank, rem)
    i1 = i0 + base + (1 if rank < rem else 0)
    return i0, i1

def midpoint_pi(nsteps, a=0.0, b=1.0, comm=MPI.COMM_WORLD):
    rank = comm.Get_rank()
    size = comm.Get_Size() if hasattr(comm, "Get_Size") else comm.Get_size()

    i0, i1 = chunk_bounds(nsteps, rank, size)
    dx = (b - a) / nsteps

    # Integral local por punto medio en [i0, i1)
    local_sum = 0.0
    for i in range(i0, i1):
        xmid = a + (i + 0.5) * dx
        local_sum += f(xmid)
    local_val = local_sum * dx

    # Reducir al root (rank 0)
    pi_est = comm.reduce(local_val, op=MPI.SUM, root=0)
    return pi_est

if __name__ == "__main__":
    import argparse
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    ap = argparse.ArgumentParser(description="por integración (punto medio) con MPI + Reduc")
    ap.add_argument("-n", "--nsteps", type=int, default=1_048_576, help="numero de subintervalos")
    args = ap.parse_args()

    comm.Barrier()
    t0 = MPI.Wtime()
    pi_est = midpoint_pi(args.nsteps, 0.0, 1.0, comm=comm)
    comm.Barrier()
    t1 = MPI.Wtime()

    if rank == 0:
        err = abs(math.pi - pi_est)
        print(f"Reduce | metodo=midpoint  nsteps={args.nsteps:,}  procs={comm.Get_size()}  tiempo={t1-t0:.3f}s")
        print(f"pi={pi_est:.12f}  | error={err:.3e}")

