#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

// Macros para calcular mínimo y máximo
#define min(a,b) ((a)<(b) ? (a) : (b))
#define max(a,b) ((a)>(b) ? (a) : (b))

// Macros para convertir coordenadas 2D (i, k) a un índice 1D para el arreglo en memoria.
// idx:  Mapeo para la matriz principal 'phi' (incluye halos).
// idxn: Mapeo para la matriz nueva 'phin' (solo zona interior).
#define idx(i,k)   (((i)-is)  *kouter + (k)-ks)
#define idxn(i,k) (((i)-is-1)*kinner + (k)-ks-1)

int main(int argc, char *argv[])
{
  // i, k: contadores de coordenadas (y, x)
  // it: contador de iteraciones de tiempo
  int i, k, it;

  // --- CONFIGURACIÓN DE SALIDA ---
  // prt=0: Desactiva imprimir la matriz en pantalla (CRÍTICO para medir tiempos reales en HPC).
  // prt_halo=0: Desactiva imprimir los bordes extra.
  int const prt=0, prt_halo=0; 
  
  // --- CONFIGURACIÓN DEL PROBLEMA ---
  // imax, kmax: Tamaño de la matriz global (N x N).
  // istart, kstart: Índices iniciales.
  // b1: Grosor del borde (halo), usualmente 1 celda.
  // itmax: Número máximo de pasos de tiempo.
  int imax=80, kmax=80; 
  int const istart=0, kstart=0, b1=1, itmax=20000;
  
  // eps: Criterio de convergencia (tolerancia).
  double const eps=1.e-08;
  
  // Variables físicas:
  // phi: Temperatura actual. phin: Temperatura nueva.
  // dx, dy: Distancia entre puntos. dt: Paso de tiempo.
  double *phi, *phin, dx,dy,dx2,dy2,dx2i,dy2i,dt,dphi,dphimax;

  // --- LECTURA DE ARGUMENTOS DE CONSOLA ---
  // Si ejecutamos "./heat_mpi 2000", imax y kmax serán 2000.
  if (argc > 1) {
      imax = atoi(argv[1]);
      kmax = imax; // Forzamos que sea cuadrada
  }

  // --- VARIABLES MPI ---
  int numprocs, my_rank;       // Total procesos, mi ID
  int right, left, upper, lower; // Ranks de mis vecinos
  MPI_Comm comm;               // Nuevo comunicador cartesiano
  int dims[2], coords[2];      // Dimensiones de la grilla de proc (ej. 4x4) y mis coords
  int period[2];               // Para saber si la grilla es cíclica (toroide)
  
  // Variables para gestionar los tamaños locales de cada sub-matriz
  int idim, kdim, icoord, kcoord;
  int isize, iinner0, in1,  ksize, kinner0, kn1; 
  int iinner, iouter, is, ie, kinner, kouter, ks, ke;
  
  // Variables auxiliares para MPI y tiempos
  int const stride=10; // Cada cuántas iteraciones chequeamos convergencia
  MPI_Request req[4];  // Solicitudes para comunicación no bloqueante
  MPI_Status statuses[4];
  
  // Tipos de datos derivados para enviar columnas (que no son contiguas en memoria)
  int gsizes[2], lsizes[2], starts[2]; 
  MPI_Datatype horizontal_border, vertical_border; 
  
  double dphimaxpartial; // Máximo local de cambio de temperatura
  double start_time, end_time, comm_time, criterion_time; // Timers

  // --- INICIO MPI ---
  MPI_Init(NULL,NULL);
  MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
  MPI_Comm_size(MPI_COMM_WORLD, &numprocs);

  // --- CREACIÓN DE LA TOPOLOGÍA CARTESIANA ---
  // MPI decide la mejor forma de organizar los procesos en una grilla 2D (ej: 16 procs -> 4x4)
  dims[0] = 0; dims[1] = 0;
  period[0] = 0; period[1] = 0; // No cíclico (sin bordes periódicos)
  MPI_Dims_create(numprocs, 2, dims);
  idim = dims[0]; kdim = dims[1]; // Dimensiones finales de la grilla de procesos

  // Crea el comunicador con estructura de grilla
  MPI_Cart_create(MPI_COMM_WORLD, 2, dims, period, 1, &comm);
  MPI_Comm_rank(comm, &my_rank); // Actualiza mi rank en el nuevo comunicador
  MPI_Cart_coords(comm, my_rank, 2, coords); // Obtiene mis coordenadas (fila, col) en la grilla de procs
  icoord = coords[0]; kcoord = coords[1];

  // Identifica quiénes son mis vecinos (Arriba, Abajo, Izq, Der)
  // Si estoy en el borde, el vecino será MPI_PROC_NULL (no existe)
  MPI_Cart_shift(comm, 0, 1, &left, &right);
  MPI_Cart_shift(comm, 1, 1, &lower, &upper);

  // --- PASO 1: DESCOMPOSICIÓN DE DOMINIO ---
  // Calculamos qué filas (is a ie) de la matriz global me tocan a mí.
  isize = imax - istart + 1; 
  iinner0 = (isize - 2*b1)  / idim; // División base
  in1 = isize - 2*b1 - idim * iinner0; // Residuo (algunos procs llevan 1 fila más)
  
  if (icoord < in1) {  
    iinner = iinner0 + 1;
    is = (istart+b1) + icoord * iinner - b1; 
  } else {             
    iinner = iinner0;
    is = istart + in1 * (iinner0+1) + (icoord-in1) * iinner;
  }
  iouter = iinner + 2*b1; // Mi tamaño total = interior + 2 bordes (halos)
  ie = is + iouter - 1;   // Índice final global

  // Lo mismo para las columnas (ks a ke)
  ksize = kmax - kstart + 1; 
  kinner0 = (ksize - 2*b1)  / kdim; 
  kn1 = ksize - 2*b1 - kdim * kinner0; 
  if (kcoord < kn1) {  
    kinner = kinner0 + 1;
    ks = (kstart+b1) + kcoord * kinner - b1; 
  } else {             
    kinner = kinner0;
    ks = kstart + kn1 * (kinner0+1) + (kcoord-kn1) * kinner;
  }
  kouter = kinner + 2*b1;
  ke = ks + kouter - 1;

  // --- SEGURIDAD: Chequeo de matriz demasiado pequeña ---
  // Si hay más procesadores que filas/columnas, el programa fallaría.
  if(((isize - 2*b1) < idim) || ((ksize - 2*b1) < kdim)) {
    if(my_rank == 0) {
        printf("ERROR: Matriz muy pequeña para tantos procesos.\n");
    }
    MPI_Finalize();
    exit(0);
  }

  // --- RESERVA DE MEMORIA ---
  // phi: Matriz local con halos.
  // phin: Matriz local nueva (sin halos).
  phi  = (double *) malloc(iouter*kouter*sizeof(double)); 
  phin = (double *) malloc(iinner*kinner*sizeof(double)); 

  // --- CREACIÓN DE TIPOS DE DATOS MPI ---
  // Necesario para enviar filas o columnas de la matriz eficientemente.
  // "vertical_border": Para enviar a Izq/Der (son columnas, no contiguas en memoria).
  gsizes[0]=iouter; gsizes[1]=kouter; 
  lsizes[0]=b1;     lsizes[1]=kinner;  starts[0]=0; starts[1]=0;
  MPI_Type_create_subarray(2, gsizes, lsizes, starts, MPI_ORDER_C, MPI_DOUBLE, &vertical_border);
  MPI_Type_commit(&vertical_border);
  
  // "horizontal_border": Para enviar a Arriba/Abajo (son filas, contiguas).
  gsizes[0]=iouter; gsizes[1]=kouter; 
  lsizes[0]=iinner; lsizes[1]=b1;      starts[0]=0; starts[1]=0;
  MPI_Type_create_subarray(2, gsizes, lsizes, starts, MPI_ORDER_C, MPI_DOUBLE, &horizontal_border);
  MPI_Type_commit(&horizontal_border);

  // --- CÁLCULO DE CONSTANTES FÍSICAS ---
  dx=1.e0/(kmax-kstart);
  dy=1.e0/(imax-istart);
  dx2=dx*dx; dy2=dy*dy;
  dx2i=1.e0/dx2; dy2i=1.e0/dy2;
  dt=min(dx2,dy2)/4.e0; // Paso de tiempo estable

  // --- CONDICIONES INICIALES ---
  // Llenar todo con 0.0
  for(i=max(1,is); i<=min(ie,imax-1); i++) { 
    for(k=ks; k<=min(ke,kmax-1); k++) {
      phi[idx(i,k)]=0.e0;
    } 
  } 

  // Condiciones de frontera (Borde derecho = 1.0)
  if (ke == kmax) { 
    for(i=is; i<=ie; i++) {
      phi[idx(i,kmax)]=1.e0;
    } 
  }

  // Condiciones de frontera (Gradiente en bordes superior e inferior)
  if (is == istart) { 
    for(k=ks; k<=min(ke,kmax-1); k++) {
      phi[idx(istart,k)] = (k-kstart)*dx;
    } 
  }
  if (ie == imax) { 
    for(k=ks; k<=min(ke,kmax-1); k++) {
      phi[idx(imax,k)] = (k-kstart)*dx;
    } 
  }

  // Iniciar Cronómetros
  start_time = MPI_Wtime();
  comm_time = 0;
  criterion_time = 0;

  // ==========================
  // === BUCLE PRINCIPAL (TIEMPO) ===
  // ==========================
  for(it=1; it<=itmax; it++) {
      dphimax=0.; // Máximo cambio local en esta iteración

      // --- CÁLCULO DE DIFERENCIAS FINITAS (STENCIL) ---
      // Solo calculamos la zona interna (sin tocar los bordes/halos)
      for(i=is+b1; i<=ie-b1; i++) {
       for(k=ks+b1; k<=ke-b1; k++) {
        // La fórmula mágica: (Vecinos - 2*Yo) / distancia^2
        dphi=(phi[idx(i+1,k)]+phi[idx(i-1,k)]-2.*phi[idx(i,k)])*dy2i
               +(phi[idx(i,k+1)]+phi[idx(i,k-1)]-2.*phi[idx(i,k)])*dx2i;
        dphi=dphi*dt;
        
        // Guardar el cambio máximo absoluto para chequear convergencia
        dphimax=max(dphimax,dphi);
        
        // Actualizar valor en matriz temporal 'phin'
        phin[idxn(i,k)]=phi[idx(i,k)]+dphi;
       } 
      } 
      
      // --- ACTUALIZACIÓN ---
      // Copiar valores de 'phin' (futuro) a 'phi' (presente)
      for(i=is+b1; i<=ie-b1; i++) {
       for(k=ks+b1; k<=ke-b1; k++) {
        phi[idx(i,k)]=phin[idxn(i,k)];
       } 
      }

    // --- PASO 2: CRITERIO DE PARADA GLOBAL (REDUCCIÓN) ---
    // Chequeamos cada 10 iteraciones (stride) para no perder tiempo comunicando siempre
    criterion_time = criterion_time - MPI_Wtime();
      if ((it % stride) == 0) { 
        if (numprocs > 1) { 
          // Cada proceso tiene su 'dphimax' local.
          // MPI_Allreduce encuentra el MAX de todos y se lo dice a todos.
          dphimaxpartial = dphimax;
          MPI_Allreduce(&dphimaxpartial, &dphimax, 1, MPI_DOUBLE, MPI_MAX, comm);
        }
        // Si el cambio máximo global es muy pequeño, el sistema se estabilizó.
        if(dphimax < eps) {
          criterion_time = criterion_time + MPI_Wtime();
          goto endOfLoop; // Romper el bucle y terminar
        }
      }
    criterion_time = criterion_time + MPI_Wtime();

    // --- PASO 3: COMUNICACIÓN DE HALOS (GHOST CELLS) ---
    // Aquí es donde los procesos intercambian sus bordes para poder calcular la siguiente iteración.
    comm_time = comm_time - MPI_Wtime();
    
    // Intercambio Arriba/Abajo
    if (kdim > 1) { 
      // Recibir del vecino de abajo y de arriba (Non-blocking receive)
      MPI_Irecv(&phi[idx(is+b1,ks)],   1,horizontal_border, lower,1,comm, &req[0]);
      MPI_Irecv(&phi[idx(is+b1,ke)],   1,horizontal_border, upper,2,comm, &req[1]);
      // Enviar al vecino de arriba y de abajo (Non-blocking send)
      MPI_Isend(&phi[idx(is+b1,ke-b1)],1,horizontal_border, upper,1,comm, &req[2]);
      MPI_Isend(&phi[idx(is+b1,ks+b1)],1,horizontal_border, lower,2,comm, &req[3]);
      // Esperar a que todo termine
      MPI_Waitall(4, req, statuses);
    }

    // Intercambio Izquierda/Derecha
    if (idim > 1) { 
      MPI_Irecv(&phi[idx(is,ks+b1)],   1,vertical_border, left, 3,comm, &req[0]);
      MPI_Irecv(&phi[idx(ie,ks+b1)],   1,vertical_border, right,4,comm, &req[1]);
      MPI_Isend(&phi[idx(ie-b1,ks+b1)],1,vertical_border, right,3,comm, &req[2]);
      MPI_Isend(&phi[idx(is+b1,ks+b1)],1,vertical_border, left, 4,comm, &req[3]);
      MPI_Waitall(4, req, statuses);
    }
    comm_time = comm_time + MPI_Wtime();

  } /* Fin del bucle for */

endOfLoop:
  end_time = MPI_Wtime(); // Parar cronómetro total

  // --- IMPRESIÓN DE RESULTADOS ---
  // Solo el proceso Maestro (Rank 0) imprime el resumen final.
  // Este formato es clave para que luego puedas leerlo con 'grep'.
  if (my_rank == 0) {
   printf("\n!numprocs=idim    iter-   wall clock time  communication part  abort criterion\n");
   printf(  "!          x kdim ations     [seconds]     method [seconds]    meth. stride [seconds]\n");
   printf(  "!%6d =%3d x%3d %6d %12.4g      %2d %12.4g    %2d %6d %12.4g\n",
          numprocs,idim,kdim,it, end_time - start_time,
                                            1, comm_time, 1, stride, criterion_time);
  }

  MPI_Finalize(); // Cerrar entorno MPI
}