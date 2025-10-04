/*
 * Copyright 1993-2010 NVIDIA Corporation.  All rights reserved.
 *
 * NVIDIA Corporation and its licensors retain all intellectual property and 
 * proprietary rights in and to this software and related documentation. 
 * Any use, reproduction, disclosure, or distribution of this software 
 * and related documentation without an express license agreement from
 * NVIDIA Corporation is strictly prohibited.
 *
 * Please refer to the applicable NVIDIA end user license agreement (EULA) 
 * associated with this source code for terms and conditions that govern 
 * your use of this NVIDIA software.
 * 
 */


//#include "../common/book.h"
#include <stdio.h>

__global__ void add( int *a, int *b, int *c ) {
    *c = *a + *b;
}

int main( void ) {
    int a,b,c;
    int *dev_a,*dev_b,*dev_c;
    int size = sizeof(int);
    cudaMalloc( (void**)&dev_a, size);
    cudaMalloc( (void**)&dev_b, size);
    cudaMalloc( (void**)&dev_c, size);
    a=100;
    b=500;
    cudaMemcpy( dev_a, &a,size, cudaMemcpyHostToDevice);
    cudaMemcpy( dev_b, &b,size, cudaMemcpyHostToDevice);
    add<<<1,1>>>( dev_a,dev_b, dev_c );
    cudaMemcpy( &c, dev_c, size, cudaMemcpyDeviceToHost);
    printf( "%i + %i = %i \n",a,b,c );
     cudaFree( dev_a ) ;
     cudaFree( dev_b ) ;
     cudaFree( dev_c ) ;

    return 0;
}


