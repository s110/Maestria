#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#define min(a,b) ((a)<(b) ? (a) : (b))
#define max(a,b) ((a)>(b) ? (a) : (b))
#define idx(i,k)  (((i)-is)  *kouter + (k)-ks)
#define idxn(i,k) (((i)-is-1)*kinner + (k)-ks-1)
int main(int argc, char *argv[])
{
// naming: i = 1st array coordinate = 1st process coordinate = y
//         k = 2nd array coordinate = 2nd process coordinate = x
//                                                    Caution: y,x and not x,y
  int i, k, it;
  int const prt=1, prt_halo=1; // 1 or 0 for printing / not printing the result / plus halos
  int const imax=80, kmax=80, istart=0, kstart=0, b1=1, itmax=20000;
  double const eps=1.e-08;
  double *phi, *phin, dx,dy,dx2,dy2,dx2i,dy2i,dt,dphi,dphimax;

// Preparation for parallelization with domain decomposition:

//   int is=istart, ie=imax, ks=kstart, ke=kmax; // now defined and calculated below

// The algortithm below is already formulated with lower and upper 
// index values (is:ie), (ks:ke) instead of (istart:imax), (kstart:kmax).
// With the MPI domain decomposition, (is:ie) and (ks:ke) will define the index rang 
// of the subdomain in a given MPI process.

// additional variables for parallelization
  int numprocs, my_rank, right, left, upper, lower, ierror;
  MPI_Comm comm;  // Cartesian communicator
  int dims[2], coords[2]; // helper variables only for MPI_CART_CREATE and ..._COORDS
  int period[2];          //                  only for MPI_CART_CREATE and ..._COORDS
  int idim, kdim, icoord, kcoord;
  int isize, iinner0, in1,  ksize, kinner0, kn1; // only for calculation of iinner, ...
  int iinner, iouter, is, ie, kinner, kouter, ks, ke;
  int ic, i_first, i_last,  kc, k_first, k_last; // only for printing
  int const stride=10; // for reduced calculation of the abort criterion
  MPI_Request req[4];
  MPI_Status statuses[4];
  int gsizes[2], lsizes[2], starts[2]; // only for MPI_Type_create_subarray
  MPI_Datatype horizontal_border, vertical_border; // datatype
  double dphimaxpartial; // for local/global calculation of the abort criterion
  double start_time, end_time, comm_time, criterion_time;

//  naming: originally: i=istart..imax,      now: i=is..ie,  icoord=0..idim-1
//          originally: k=kstart..kmax,      now: k=ks..ke,  kcoord=0..kdim-1
//                      with istart=kstart=0      s=start index,  e=end index

  MPI_Init(NULL,NULL);
  MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
  MPI_Comm_size(MPI_COMM_WORLD, &numprocs);

// the 2-dimensional domain decomposition:

  dims[0] = 0; dims[1] = 0;
  period[0] = 0; period[1] = 0;
  MPI_Dims_create(numprocs, 2, dims);
  idim = dims[0];
  kdim = dims[1];
  MPI_Cart_create(MPI_COMM_WORLD,2,dims,period,1,&comm);
  MPI_Comm_rank(comm, &my_rank);
  MPI_Cart_coords(comm, my_rank, 2, coords);
  icoord = coords[0];
  kcoord = coords[1];
  MPI_Cart_shift(comm, 0, 1, &left, &right);
   // the ranks (left,right) represent the coordinates ((icoord-1,kcoord), (icoord+1,kcoord)) 
  MPI_Cart_shift(comm, 1, 1, &lower,&upper);
   // the ranks (lower,upper) represent the coordinates ((icoord,kcoord-1),(icoord,kcoord+1)) 

// Step 1: calculating the own subdomain in each process
// --------------------------------------------------------------
//
// whole y indecees   |------------- isize = imax-istart+1 ------------|
//    start/end index  ^-istart                                  imax-^
// 
// 1. interval        |--- iouter1---|   
//                    |--|--------|--|
//                     b1  iinner1 b1 
//    start/end index  ^-is      ie-^ 
// 2. interval                 |--|--------|--|   
// 3. interval                          |--|--------|--| 
// 4. interval                                   |--|-------|--| 
//                                                   iinner0 = iinner1 - 1
// 5. interval = idim's interval                         |--|-------|--|
//
// In each iteration on each interval, the inner area is computed
// by using the values of the last iteration in the whole outer area. 
//
// icoord = number of the interval - 1
// 
// To fit exactly into isize, we use in1 intervals of with iinner1 = iinner0 + 1
// and (idim-in1) intervals of with iinner0 
//
//         Originally:     And as result of the domain decomposition into idim subdomains:
// isize = imax-istart+1 = 2*b1 + in1*iinner1 + (idim-in1)*inner0
//
// computing is:ie, ks:ke
//   - input:            istart, imax, b1, idim, icoord (and k...)
//   - to be calculated: is, ie, iinner, iouter
//   - helper variables: iinner0, in1, isize

  isize = imax - istart + 1; // total number of elements, including the "2*b1" boundary elements
  // isize - 2*b1 = total number of unknowns
  iinner0 = (isize - 2*b1)  / idim; // smaller inner size through divide with rounding off
  in1 = isize - 2*b1 - idim * iinner0; // number of processes that must have "inner0+1" unknowns
  if (icoord < in1) {  // the first in1 processes will have "iinner0+1" unknowns
    iinner = iinner0 + 1;
    is = (istart+b1) + icoord * iinner - b1; // note that "is" reflects the position of the 
                                             // first halo or boundary element of the subdomain
  } else {             // and all other processes will have iinner0 unknowns
    iinner = iinner0;
    is = istart + in1 * (iinner0+1) + (icoord-in1) * iinner;
  }
  iouter = iinner + 2*b1;
  ie = is + iouter - 1;

// same for x coordinate: 
  ksize = kmax - kstart + 1; // total number of elements, including the "2*b1" boundary elements
  // ksize - 2*b1 = total number of unknowns
  kinner0 = (ksize - 2*b1)  / kdim; // smaller inner size through divide with rounding off
  kn1 = ksize - 2*b1 - kdim * kinner0; // number of processes that must have "knner0+1" unknowns
  if (kcoord < kn1) {  // the first kn1 processes will have "kinner0+1" unknowns
    kinner = kinner0 + 1;
    ks = (kstart+b1) + kcoord * kinner - b1; // note that "ks" reflects the position of the 
                                             // first halo or boundary element of the subdomain
  } else {             // and all other will have kinner0 unknowns
    kinner = kinner0;
    ks = kstart + kn1 * (kinner0+1) + (kcoord-kn1) * kinner;
  }
  kouter = kinner + 2*b1;
  ke = ks + kouter - 1;

  if (my_rank == 0) {
    printf("\n isize=%3d idim=%3d || in1*(iinner0+1)=%3d *%3d + (idim-in1)*iinner0=%3d *%3d + 2*b1=2*%1d || sum = %3d\n",
               isize,    idim,       in1, iinner0+1,             idim-in1, iinner0,             b1,
                                                                            in1*(iinner0+1) + (idim-in1)*iinner0 + 2*b1);
    printf("\n ksize=%3d kdim=%3d || kn1*(kinner0+1)=%3d *%3d + (kdim-kn1)*kinner0=%3d *%3d + 2*b1=2*%1d || sum = %3d\n",
               ksize,    kdim,       kn1, kinner0+1,             kdim-kn1, kinner0,             b1,
                                                                            kn1*(kinner0+1) + (kdim-kn1)*kinner0 + 2*b1);
  }



// It must be guaranteed that the array 'phin' is not an empty array,
// i.e., that the iinner in all processes is at least 1,
// i.e., the total number of unknowns in direction "i" is at least 1*idim, and same for k, 
// because otherwise, the halo communication would not work.
// Note that all processes have to make the same decision. Therefore they should
// use "isize,ksize" and "idim,kdim" and cannot use only their own "iinner,kinner".
  if(((isize - 2*b1) < idim) ||
     ((ksize - 2*b1) < kdim)) {
    if(my_rank == 0) {
        printf("phin is in some processes an empty array because isize-2*b1=%3d < idim=%3d or ksize-2*b1=%3d < kdim=%3d\n",
                                                                 isize-2*b1,      idim,       ksize-2*b1,      kdim);
    }
    MPI_Finalize();
    exit(0);
  }

  phi  = (double *) malloc(iouter*kouter*sizeof(double)); // index range: (is:ie,ks:ke)
  phin = (double *) malloc(iinner*kinner*sizeof(double)); // index range: (is+b1:ie-b1,ks+b1:ke-b1)

// create and commit derived datatypes vertical_border and horizontal_border through MPI_Type_vector()
//  MPI_Type_vector(b1,kinner,kouter, MPI_DOUBLE, &vertical_border);
//  MPI_Type_commit(&vertical_border);
//  MPI_Type_vector(iinner,b1,kouter, MPI_DOUBLE, &horizontal_border);
//  MPI_Type_commit(&horizontal_border);

// Step 4: Advanced exercise:  Same as with MPI_Type_vector(), but with MPI_Type_create_subarray()
// ----------------------------------   (advantage: would work alsowith 3,4, ... dimensions)
//
  gsizes[0]=iouter; gsizes[1]=kouter; 
  lsizes[0]=b1;     lsizes[1]=kinner;  starts[0]=0; starts[1]=0;
  MPI_Type_create_subarray(2, gsizes, lsizes, starts, MPI_ORDER_C, MPI_DOUBLE, &vertical_border);
  MPI_Type_commit(&vertical_border);
  gsizes[0]=iouter; gsizes[1]=kouter; 
  lsizes[0]=iinner; lsizes[1]=b1;      starts[0]=0; starts[1]=0;
  MPI_Type_create_subarray(2, gsizes, lsizes, starts, MPI_ORDER_C, MPI_DOUBLE, &horizontal_border);
  MPI_Type_commit(&horizontal_border);


// naming: i = 1st array coordinate = 1st process coordinate = y
//         k = 2nd array coordinate = 2nd process coordinate = x
//                                                    Caution: y,x and not x,y
  dx=1.e0/(kmax-kstart);
  dy=1.e0/(imax-istart);
  dx2=dx*dx;
  dy2=dy*dy;
  dx2i=1.e0/dx2;
  dy2i=1.e0/dy2;
  dt=min(dx2,dy2)/4.e0;
// start values 0.d0 
  for(i=max(1,is); i<=min(ie,imax-1); i++) { // do not overwrite the boundary condition
    for(k=ks; k<=min(ke,kmax-1); k++) {
      phi[idx(i,k)]=0.e0;
    } /*for*/
  } /*for*/
// start values 1.d0
 if (ke == kmax) { 
  for(i=is; i<=ie; i++) {
    phi[idx(i,kmax)]=1.e0;
  } /*for*/
 }
// start values dx
 if (is == istart) { 
//       phi[idx(0,0)]=0.d0
//       for(k=1; k<=kmax-1 ; k++) { 
//         phi[idx(0,k)]=phi[idx(0,k-1)]+dx 
//         phi[idx(imax,k)]=phi[idx(imax,k-1)]+dx 
//       } /*for*/ 
//       ... substitute algorithmus by a code, 
//           that can be computed locally: 
  for(k=ks; k<=min(ke,kmax-1); k++) {
    phi[idx(istart,k)] = (k-kstart)*dx;
  } /*for*/
 }
 if (ie == imax) { 
  for(k=ks; k<=min(ke,kmax-1); k++) {
    phi[idx(imax,k)] = (k-kstart)*dx;
  } /*for*/
 }

// print details
 if (my_rank == 0) {
    printf("\nHeat Conduction 2d\n");
    printf("\ndx =%12.4e, dy =%12.4e, dt=%12.4e, eps=%12.4e\n", dx, dy, dt, eps); 
 }
  start_time = MPI_Wtime();
  comm_time = 0;
  criterion_time = 0;

// iteration
  for(it=1; it<=itmax; it++) {
      dphimax=0.;
      for(i=is+b1; i<=ie-b1; i++) {
       for(k=ks+b1; k<=ke-b1; k++) {
        dphi=(phi[idx(i+1,k)]+phi[idx(i-1,k)]-2.*phi[idx(i,k)])*dy2i
               +(phi[idx(i,k+1)]+phi[idx(i,k-1)]-2.*phi[idx(i,k)])*dx2i;
        dphi=dphi*dt;
        dphimax=max(dphimax,dphi);
        phin[idxn(i,k)]=phi[idx(i,k)]+dphi;
       } /*for*/
      } /*for*/
// save values
      for(i=is+b1; i<=ie-b1; i++) {
       for(k=ks+b1; k<=ke-b1; k++) {
        phi[idx(i,k)]=phin[idxn(i,k)];
       } /*for*/
      } /*for*/

// Step 2: common abort criterion for all processes
// ---------------------------------------------------------
//
// for optimization: allreduce only each stride's loop:
    criterion_time = criterion_time - MPI_Wtime();
      if ((it % stride) == 0) { 
        if (numprocs > 1) { 
          // the following code is necessary, because each process only calculates a local (and not global) dphimax
          dphimaxpartial = dphimax;
          MPI_Allreduce(&dphimaxpartial, &dphimax, 1, MPI_DOUBLE, MPI_MAX, comm);
        }
        if(dphimax < eps) {
          criterion_time = criterion_time + MPI_Wtime();
          goto endOfLoop; // Finish the timestep loop "do it=…"
        }
      }
    criterion_time = criterion_time + MPI_Wtime();

// Step 3: the halo communication
// ---------------------------------------
//
    comm_time = comm_time - MPI_Wtime();
// send and receive to/from upper/lower
    if (kdim > 1) { // otherwise in all processes both, lower and upper are MPI_PROC_NULL
      MPI_Irecv(&phi[idx(is+b1,ks)],   1,horizontal_border, lower,1,comm, &req[0]);
      MPI_Irecv(&phi[idx(is+b1,ke)],   1,horizontal_border, upper,2,comm, &req[1]);
      MPI_Isend(&phi[idx(is+b1,ke-b1)],1,horizontal_border, upper,1,comm, &req[2]);
      MPI_Isend(&phi[idx(is+b1,ks+b1)],1,horizontal_border, lower,2,comm, &req[3]);
      MPI_Waitall(4, req, statuses);
      // or alternatively with sendrecv:
      // MPI_Sendrecv(&phi[idx(is+b1,ke-b1)],1,horizontal_border, upper,1,
      //              &phi[idx(is+b1,ks)],   1,horizontal_border, lower,1, comm, MPI_STATUS_IGNORE);
      // MPI_Sendrecv(&phi[idx(is+b1,ks+b1)],1,horizontal_border, lower,2,
      //              &phi[idx(is+b1,ke)],   1,horizontal_border, upper,2, comm, MPI_STATUS_IGNORE);
    }

// send and receive to/from left/right
    if (idim > 1) { // otherwise in all processes both, left and right are MPI_PROC_NULL
      MPI_Irecv(&phi[idx(is,ks+b1)],   1,vertical_border, left, 3,comm, &req[0]);
      MPI_Irecv(&phi[idx(ie,ks+b1)],   1,vertical_border, right,4,comm, &req[1]);
      MPI_Isend(&phi[idx(ie-b1,ks+b1)],1,vertical_border, right,3,comm, &req[2]);
      MPI_Isend(&phi[idx(is+b1,ks+b1)],1,vertical_border, left, 4,comm, &req[3]);
      MPI_Waitall(4, req, statuses);
      // or alternatively with sendrecv:
      // MPI_Sendrecv(&phi[idx(ie-b1,ks+b1)],1,vertical_border, right,3,
      //              &phi[idx(is,ks+b1)],   1,vertical_border, left, 3, comm, MPI_STATUS_IGNORE);
      // MPI_Sendrecv(&phi[idx(is+b1,ks+b1)],1,vertical_border, left, 4,
      //              &phi[idx(ie,ks+b1)],   1,vertical_border, right,4, comm, MPI_STATUS_IGNORE);
    }
    comm_time = comm_time + MPI_Wtime();

  } /*for*/
endOfLoop:
  end_time = MPI_Wtime();

  if (prt) {
    for(ic = 0; ic <= idim-1; ic++) {
      for(kc = 0; kc <= kdim-1; kc++) {
        if ((ic == icoord) && (kc == kcoord)) { 
          i_first = is ;
          i_last  = ie ;
          k_first = ks ;
          k_last  = ke ;
          if (! prt_halo) {
            if (ic > 0) i_first = is + b1;     // do not print halo at the beginning
            if (ic < idim-1) i_last = ie - b1; // do not print halo at the end
            if (kc > 0) k_first = ks + b1;     // do not print halo at the beginning
            if (kc < kdim-1) k_last = ke - b1; // do not print halo at the end
          }
          if (kc == 0) {
              printf("\nprinting the %3dth horizontal block\n", ic);
              printf("               i=");
              for (i=i_first; i<=i_last; i++) printf(" %4d",i); printf("\n");
          } else {
            if (prt_halo)  printf("\n"); // additional empty line between the processes
          }
          for(k=k_first; k<=k_last; k++) {
              printf("ic=%2d kc=%2d k=%3d", ic, kc, k);
              for (i=i_first; i<=i_last; i++) printf(" %4.2f", phi[idx(i,k)]); printf("\n");
          } /*for*/
        }
        MPI_Barrier(comm); // to separate the printing of each block by different processes.
                           // Caution: This works in most cases, but does not guarantee that the
                           //          output lines on the common stdout are in the expected sequence.
      } /*for*/
    } /*for*/
  } /*if prt*/

  if (my_rank == 0) {
   printf("\n!numprocs=idim    iter-   wall clock time  communication part  abort criterion\n");
   printf(  "!          x kdim ations     [seconds]     method [seconds]    meth. stride [seconds]\n");
   printf(  "!%6d =%3d x%3d %6d %12.4g      %2d %12.4g    %2d %6d %12.4g\n",
          numprocs,idim,kdim,it, end_time - start_time,
                                            1, comm_time, 1, stride, criterion_time);
  }





  MPI_Finalize();

}
