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

// *********************************************************************
// oclVectorAdd Notes:  
//
// A simple OpenCL API demo application that implements 
// element by element vector addition between 2 float arrays. 
//
// Runs computations with OpenCL on the GPU device and then checks results 
// against basic host CPU/C++ computation.
//
// Uses some 'shr' and 'ocl' functions from oclUtils and shrUtils libraries for 
// compactness, but these are NOT required libs for OpenCL developement in general.
// *********************************************************************
// common SDK header for standard utilities and system libs 
#include <oclUtils.h>
#include <shrQATest.h>
#include <time.h>

// Name of the file with the source code for the computation kernel
// *********************************************************************
const char *cSourceFile = "VarInc.c";

// Host buffers for demo
// *********************************************************************

// OpenCL Vars
cl_context cxGPUContext;        // OpenCL context
cl_command_queue cqCommandQueue;        // OpenCL command que
cl_platform_id cpPlatform;      // OpenCL platform
cl_device_id cdDevice;          // OpenCL device
cl_program cpProgram;           // OpenCL program
cl_kernel ckKernel;             // OpenCL kernel
cl_mem cmDevCounters;               // OpenCL device source buffer A
size_t szGlobalWorkSize;        // 1D var for Total # of work items
size_t szLocalWorkSize;		    // 1D var for # of work items in the work group	
size_t szParmDataBytes;			// Byte size of context information
size_t szKernelLength;			// Byte size of kernel code
cl_int ciErr1, ciErr2;			// Error code var
char *cPathAndName = NULL;      // var for full paths to data, src, etc.
char *cSourceCL = NULL;         // Buffer to hold source for compilation
const char *cExecutableName = NULL;

// demo config vars
shrBOOL bNoPrompt = shrFALSE;

#define COUNTER_MAX  1000000
#define COUNTER_NUM      100
unsigned int counterNum = COUNTER_NUM;
unsigned int counterMax = COUNTER_MAX;

void *counters;
unsigned int counters2[COUNTER_NUM];        // Host buffers for OpenCL test


void
Cleanup(int argc, char **argv, int iExitCode);

// Main function 
// *********************************************************************
int
main(int argc, char **argv)
{

  clock_t procTimeCL;
  clock_t procTimeC;

  shrQAStart(argc, argv);

  // get command line arg for quick test, if provided
  bNoPrompt = shrCheckCmdLineFlag(argc, (const char**) argv, "noprompt");

  // start logs
  cExecutableName = argv[0];
  shrSetLogFileName("oclVectorAdd.txt");
  shrLog("%s Starting...\n\n# of float elements per Array \t= %i\n", argv[0],
    COUNTER_NUM);

  // set and log Global and Local work size dimensions
  szLocalWorkSize = 300;
  szGlobalWorkSize = shrRoundUp((int) szLocalWorkSize, COUNTER_NUM); // rounded up to the nearest multiple of the LocalWorkSize
  shrLog(
      "Global Work Size \t\t= %u\nLocal Work Size \t\t= %u\n# of Work Groups \t\t= %u\n\n",
      szGlobalWorkSize,
      szLocalWorkSize,
      (szGlobalWorkSize % szLocalWorkSize + szGlobalWorkSize / szLocalWorkSize));

  // Allocate and initialize host arrays
  shrLog("Allocate and Init Host Mem...\n");
  counters = (void*) malloc(sizeof(cl_int) * szGlobalWorkSize);

  //Get an OpenCL platform
  ciErr1 = clGetPlatformIDs(1, &cpPlatform, NULL);

  shrLog("clGetPlatformID...\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error in clGetPlatformID, Line %u in file %s !!!\n\n", __LINE__,
           __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }

  //Get the devices
  ciErr1 = clGetDeviceIDs(cpPlatform, CL_DEVICE_TYPE_GPU, 1, &cdDevice, NULL);
  shrLog("clGetDeviceIDs...\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error in clGetDeviceIDs, Line %u in file %s !!!\n\n", __LINE__,
           __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }

  //Create the context
  cxGPUContext = clCreateContext(0, 1, &cdDevice, NULL, NULL, &ciErr1);
  shrLog("clCreateContext...\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error in clCreateContext, Line %u in file %s !!!\n\n", __LINE__,
           __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }

  // Create a command-queue
  cqCommandQueue = clCreateCommandQueue(cxGPUContext, cdDevice, 0, &ciErr1);
  shrLog("clCreateCommandQueue...\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error in clCreateCommandQueue, Line %u in file %s !!!\n\n",
           __LINE__, __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }

  // Allocate the OpenCL buffer memory objects for source and result on the device GMEM
  cmDevCounters = clCreateBuffer(cxGPUContext, CL_MEM_WRITE_ONLY,
                                 sizeof(cl_int) * COUNTER_NUM, NULL, &ciErr1);
  shrLog("clCreateBuffer...\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error %d in clCreateBuffer, Line %u in file %s !!!\n\n", ciErr1, __LINE__,
           __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }

  // Read the OpenCL kernel in from source file
  shrLog("oclLoadProgSource (%s)...\n", cSourceFile);
  cPathAndName = shrFindFilePath(cSourceFile, argv[0]);
  cSourceCL = oclLoadProgSource(cPathAndName, "", &szKernelLength);

  // Create the program
  cpProgram = clCreateProgramWithSource(cxGPUContext, 1,
                                        (const char**) &cSourceCL,
                                        &szKernelLength, &ciErr1);
  shrLog("clCreateProgramWithSource...\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error in clCreateProgramWithSource, Line %u in file %s !!!\n\n",
           __LINE__, __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }

  // Build the program with 'mad' Optimization option
#ifdef MAC
        char* flags = "-cl-fast-relaxed-math -DMAC";
    #else
  char *flags = "-cl-fast-relaxed-math";
#endif
  ciErr1 = clBuildProgram(cpProgram, 0, NULL, NULL, NULL, NULL);
  shrLog("clBuildProgram...\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error in clBuildProgram, Line %u in file %s !!!\n\n", __LINE__,
           __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }

  // Create the kernel
  ckKernel = clCreateKernel(cpProgram, "VarInc", &ciErr1);
  shrLog("clCreateKernel (VectorAdd)...\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error %d in clCreateKernel, Line %u in file %s !!!\n\n", ciErr1, __LINE__,
           __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }

  // Set the Argument values
  ciErr1 = clSetKernelArg(ckKernel, 0, sizeof(cl_mem), (void*) &cmDevCounters);
  ciErr1 |= clSetKernelArg(ckKernel, 1, sizeof(cl_int), (void*) &counterMax);
  ciErr1 |= clSetKernelArg(ckKernel, 2, sizeof(cl_int), (void*) &counterNum);

  shrLog("clSetKernelArg 0 - 3...\n\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error in clSetKernelArg, Line %u in file %s !!!\n\n", __LINE__,
           __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }


  procTimeCL = clock();
  // --------------------------------------------------------
  // Start Core sequence... copy input data to GPU, compute, copy results back

  // Asynchronous write of data to GPU device
  ciErr1 = clEnqueueWriteBuffer(cqCommandQueue, cmDevCounters, CL_FALSE, 0,
                                sizeof(cl_int) * COUNTER_NUM, counters, 0,
                                NULL, NULL);
  shrLog("clEnqueueWriteBuffer)...\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error in clEnqueueWriteBuffer, Line %u in file %s !!!\n\n",
           __LINE__, __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }

  shrLog("clEnqueueNDRangeKernel (VarInc)...\n");
  ciErr1 = 0;


  // Launch kernel
  ciErr1 != clEnqueueNDRangeKernel(cqCommandQueue, ckKernel, 1, NULL,
                                &szGlobalWorkSize, &szLocalWorkSize, 0, NULL, NULL);

  clFinish(cqCommandQueue);


  if(ciErr1 != CL_SUCCESS){
    shrLog("Error in clEnqueueNDRangeKernel, Line %u in file %s !!!\n\n",
           __LINE__, __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }



  // Synchronous/blocking read of results, and check accumulated errors
  ciErr1 = clEnqueueReadBuffer(cqCommandQueue, cmDevCounters, CL_TRUE, 0,
                               sizeof(cl_int) * COUNTER_NUM, counters, 0,
                               NULL, NULL);

  procTimeCL = clock() - procTimeCL;

  shrLog("clEnqueueReadBuffer (Dst)...\n\n");
  if(ciErr1 != CL_SUCCESS){
    shrLog("Error %d in clEnqueueReadBuffer, Line %u in file %s !!!\n\n", ciErr1, __LINE__,
           __FILE__);
    Cleanup(argc, argv, EXIT_FAILURE);
  }
  //--------------------------------------------------------

  for(int i = 0; i < 3; i++){
    shrLog("counters(%d): %d \n", i, *(int*) (counters + i * sizeof(int)));
  }

  // Compute and compare results for golden-host and report errors and pass/fail
  shrLog("Comparing against Host/C++ computation...\n\n");
  shrBOOL bMatch = shrTRUE;

  procTimeC = clock();

  for(int i = 0; i < COUNTER_MAX; i++){
    for(int j = 0; j < COUNTER_NUM; j++){
      counters2[j] = counters2[j] + 1;
    }
  }
  procTimeC = clock() - procTimeC;

  for(int i = 0; i < 3; i++){
    shrLog("counters2(%d): %d \n", i, counters2[i]);
  }

  printf("\nElapsed CL: %f seconds\n", (double)(procTimeCL) / CLOCKS_PER_SEC);
  printf("Elapsed  C: %f seconds\n", (double)(procTimeC) / CLOCKS_PER_SEC);


  // Cleanup and leave
  Cleanup(argc, argv, (bMatch == shrTRUE) ? EXIT_SUCCESS : EXIT_FAILURE);
}

void
Cleanup(int argc, char **argv, int iExitCode)
{
  // Cleanup allocated objects
  shrLog("Starting Cleanup...\n\n");
  if(cPathAndName)
    free(cPathAndName);
  if(cSourceCL)
    free(cSourceCL);
  if(ckKernel)
    clReleaseKernel(ckKernel);
  if(cpProgram)
    clReleaseProgram(cpProgram);
  if(cqCommandQueue)
    clReleaseCommandQueue(cqCommandQueue);
  if(cxGPUContext)
    clReleaseContext(cxGPUContext);
  if(cmDevCounters)
    clReleaseMemObject(cmDevCounters);

  // Free host memory
  free(counters);


}


