#include <stdio.h>
#include <stdlib.h>
#include <time.h>
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
  int const prt=1; // 1 or 0 for printing / not printing the result
  int const imax=80, kmax=80, istart=0, kstart=0, b1=1, itmax=20000;
  double const eps=1.e-08;
  double *phi, *phin, dx,dy,dx2,dy2,dx2i,dy2i,dt,dphi,dphimax;
  clock_t t;

// Preparation for parallelization with domain decomposition:
  int is=istart, ie=imax, ks=kstart, ke=kmax; // now defined and calculated below
  int iouter=ie-is+1, kouter=ke-ks+1, iinner=iouter-2*b1, kinner=kouter-2*b1;

// The algortithm below is already formulated with lower and upper 
// index values (is:ie), (ks:ke) instead of (istart:imax), (kstart:kmax).
// With the MPI domain decomposition, (is:ie) and (ks:ke) will define the index rang 
// of the subdomain in a given MPI process.

  phi  = (double *) malloc(iouter*kouter*sizeof(double)); // index range: (is:ie,ks:ke)
  phin = (double *) malloc(iinner*kinner*sizeof(double)); // index range: (is+b1:ie-b1,ks+b1:ke-b1)
//         
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
    printf("\nHeat Conduction 2d\n");
    printf("\ndx =%12.4e, dy =%12.4e, dt=%12.4e, eps=%12.4e\n", dx, dy, dt, eps); 

  t=clock();

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

      if(dphimax < eps) {
          goto endOfLoop; // Finish the timestep loop "do it=…"
      }

  } /*for*/
endOfLoop:

  t=clock();

  if (prt) {
          printf("   i=");
          for (i=is; i<=ie; i++) printf(" %4d",i); printf("\n");
          for(k=ks; k<=ke; k++) {
              printf("k=%3d", k);
              for (i=is; i<=ie; i++) printf(" %4.2f", phi[idx(i,k)]); printf("\n");
          } /*for*/
  } /*if prt*/

  printf("\n%d iterations\n",it);
  printf("\nCPU time = %#12.4g sec\n",t/1000000.0);





}
