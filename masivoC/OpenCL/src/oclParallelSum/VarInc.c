/*
 * Copyright 1993-2010 NVIDIA Corporation.  All rights reserved.
 *
 * Please refer to the NVIDIA end user license agreement (EULA) associated
 * with this source code for terms and conditions that govern your use of
 * this software. Any use, reproduction, disclosure, or distribution of
 * this software and related documentation outside the terms of the EULA
 * is strictly prohibited.
 *
 */
 
 // OpenCL Kernel Function for element by element vector addition
#ifndef __OPENCL_VERSION__
#define __kernel
#define __global
#endif



__kernel void VarInc(
    __global unsigned int *counters,
    unsigned int count_to,
    unsigned int iNumElements
    )
{
  int gid = get_global_id(0);

  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (gid >= iNumElements)
  {
    return;
  }

  for(int j = 0; j < count_to; j++){
    counters[gid] = counters[gid] + 1;
  }
}
