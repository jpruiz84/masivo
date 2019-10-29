#define __CL_ENABLE_EXCEPTIONS

#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <string.h>

#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <shrUtils.h>
#include <oclUtils.h>

// All OpenCL headers
#if defined (__APPLE__) || defined(MACOSX)
    #include <OpenCL/opencl.h>
#else
    #include <CL/opencl.h>
#endif


#define STOPS_NUM                    3000
#define STOP_MAX_PASS                10000
#define MAX_SIM_TIME               8*3600     // In secs, 8 hours
#define PASS_TOTAL_ARRIVAL_TIME    3600     // In secs

#define PRINT_LIST      0
#define USE_OPENCL      1

typedef struct {
  unsigned int    passId;
  unsigned short  origStop;
  unsigned short  destStop;
  unsigned short  arrivalTime;
  unsigned short  alightTime;
  unsigned int    status;
} PASS_TYPE;


typedef struct {
  unsigned short  stopNum;
  unsigned int    total;
  unsigned int    lastEmtpy;
  unsigned int    wIndex;
  PASS_TYPE       pass[STOP_MAX_PASS];
} SL_TYPE;

enum PASS_STATUS{
  PASS_STATUS_EMPTY,
  PASS_STATUS_TO_ARRIVE,
  PASS_STATUS_ARRIVED,
  PASS_STATUS_IN_BUS,
  PASS_STATUS_ALIGHTED,
};

SL_TYPE stopsArrivalList[STOPS_NUM];
SL_TYPE stopsQueueList[STOPS_NUM];

static cl_command_queue command_queue;
static cl_context context;
static cl_device_id cdDevice;
char device_string[1024];
cl_kernel test1;


void checkErr( cl_int err,int line, const char *n,  bool verbosity=false ) {
  if( err != CL_SUCCESS ) {
    std::cerr << n << "\r\t\t\t\t\t\tline:" << line<<" "<<oclErrorString(err) << std::endl;
      assert(0);
  }
  else if( n != NULL ) {
      if( verbosity) std::cerr << n << "\r\t\t\t\t\t\t" << "OK" <<std::endl;

  }
}

int
opencl_init(int devId)
{

  // Get OpenCL platform ID for NVIDIA if avaiable, otherwise default
  shrLog("OpenCL SW Info:\n\n");
  char cBuffer[1024];
  cl_platform_id clSelectedPlatformID = NULL;
  cl_int ciErrNum = oclGetPlatformID(&clSelectedPlatformID);
  oclCheckError(ciErrNum, CL_SUCCESS);

  // Get OpenCL platform name and version
  ciErrNum = clGetPlatformInfo(clSelectedPlatformID, CL_PLATFORM_NAME,
                               sizeof(cBuffer), cBuffer, NULL);
  if(ciErrNum == CL_SUCCESS){
    shrLog(" CL_PLATFORM_NAME: \t%s\n", cBuffer);
  }
  else{
    shrLog(" Error %i in clGetPlatformInfo Call !!!\n\n", ciErrNum);
  }

  ciErrNum = clGetPlatformInfo(clSelectedPlatformID, CL_PLATFORM_VERSION,
                               sizeof(cBuffer), cBuffer, NULL);
  if(ciErrNum == CL_SUCCESS){
    shrLog(" CL_PLATFORM_VERSION: \t%s\n", cBuffer);
  }
  else{
    shrLog(" Error %i in clGetPlatformInfo Call !!!\n\n", ciErrNum);
  }

  // Log OpenCL SDK Revision #
  shrLog(" OpenCL SDK Revision: \t%s\n\n\n", OCL_SDKREVISION);

  // Get and log OpenCL device info
  cl_uint ciDeviceCount;
  cl_device_id *devices;
  shrLog("OpenCL Device Info:\n\n");
  ciErrNum = clGetDeviceIDs(clSelectedPlatformID, CL_DEVICE_TYPE_ALL, 0, NULL,
                            &ciDeviceCount);

  // check for 0 devices found or errors...
  if(ciDeviceCount == 0){
    shrLog(" No devices found supporting OpenCL (return code %i)\n\n",
           ciErrNum);
  }
  else if(ciErrNum != CL_SUCCESS){
    shrLog(" Error %i in clGetDeviceIDs call !!!\n\n", ciErrNum);
  }
  else{
    // Get and log the OpenCL device ID's
    char cTemp[2];
    sprintf(cTemp, "%u", ciDeviceCount);
    if((devices = (cl_device_id*) malloc(sizeof(cl_device_id) * ciDeviceCount))
        == NULL){
      shrLog(" Failed to allocate memory for devices !!!\n\n");
    }
    ciErrNum = clGetDeviceIDs(clSelectedPlatformID, CL_DEVICE_TYPE_ALL,
                              ciDeviceCount, devices, &ciDeviceCount);
    if(ciErrNum == CL_SUCCESS){
      //Create a context for the devices
      cl_context_properties props[] =
        {
#ifdef _WIN32
            CL_CONTEXT_PLATFORM, (cl_context_properties)clSelectedPlatformID,
            CL_GL_CONTEXT_KHR, (cl_context_properties)wglGetCurrentContext(),
            CL_WGL_HDC_KHR, (cl_context_properties)wglGetCurrentDC(),
#else
            CL_CONTEXT_PLATFORM, (cl_context_properties) clSelectedPlatformID,
#endif
            0 };

      if(ciDeviceCount > 1){
        ciDeviceCount = 1;
        shrLog(
            "Note: Multiple device found, but creating context for first device only.\n");
      }
      shrLog("Creating context on device %d\n", devId);
      context = clCreateContext(props, ciDeviceCount, &devices[devId], NULL,
                                NULL, &ciErrNum);
      if(ciErrNum != CL_SUCCESS){
        shrLog("Error %i in clCreateContext call !!!\n\n", ciErrNum);
      }
    }
  }

  cdDevice = devices[devId];

  // Create a command-queue on the GPU device
  // enable profiling by sending the CL_QUEUE_PROFILING_ENABLE flag
  command_queue = clCreateCommandQueue(context, cdDevice,
                                       CL_QUEUE_PROFILING_ENABLE, &ciErrNum);
  checkErr(ciErrNum, __LINE__, "clCreateCommandQueue");

  cl_bool img_support = false;
  ciErrNum = clGetDeviceInfo(cdDevice, CL_DEVICE_IMAGE_SUPPORT, sizeof(cl_bool),
                             &img_support, NULL);
  checkErr(ciErrNum, __LINE__, "clGetDeviceInfo");
  if(img_support){
    printf("CL_DEVICE_IMAGE_SUPPORT Found.\n");
  }
  else{
    printf("CL_DEVICE_IMAGE_SUPPORT **Missing**\n");
  }
  size_t n;
  ciErrNum = clGetDeviceInfo(cdDevice, CL_DEVICE_NAME, 1024, device_string, &n);

  size_t retsz;
  cl_device_type dtype;
  ciErrNum = clGetDeviceInfo(cdDevice, CL_DEVICE_TYPE, sizeof(cl_device_type),
                             &dtype, &retsz);
  checkErr(ciErrNum, __LINE__, "clGetDeviceInfo");
  assert(dtype == CL_DEVICE_TYPE_GPU);
  printf("type is GPU\n");

  return 0;
}

// build a program from a file, uses global device, and given context
cl_program buildProgramFromFile(cl_context clctx, const char *source_path)
{
  cl_int err;
  // Buffer to hold source for compilation
  size_t program_length;
  //char source_path[] = "lkflow.cl";
  const char *source = oclLoadProgSource(source_path, "", &program_length );
  if( source == NULL ) {
    fprintf(stderr, "Missing source file %s?\n", source_path);
  }

  // Create OpenCL program with source code
  cl_program program = clCreateProgramWithSource(clctx, 1, &source, NULL, &err);
  checkErr(err, __LINE__,"clCreateProgramWithSource");

  // Build the program (OpenCL JIT compilation)
  std::cerr<<"Calling clBuildProgram..."<<std::endl;
  err = clBuildProgram(program, 1, &cdDevice, NULL, NULL, NULL);
  std::cerr<<"OK"<<std::endl;

  cl_build_status build_status;
  err = clGetProgramBuildInfo(program, cdDevice,
    CL_PROGRAM_BUILD_STATUS, sizeof(cl_build_status), &build_status, NULL);
  checkErr(err, __LINE__, "clGetProgramBuildInfo");

  char *build_log;
  size_t ret_val_size;
  err = clGetProgramBuildInfo(program, cdDevice, CL_PROGRAM_BUILD_LOG, 0, NULL, &ret_val_size);
  checkErr(err,__LINE__, "clGetProgramBuildInfo");
  build_log = (char *)malloc(ret_val_size+1);
  err = clGetProgramBuildInfo(program, cdDevice, CL_PROGRAM_BUILD_LOG, ret_val_size, build_log, NULL);
  checkErr(err, __LINE__,"clGetProgramBuildInfo");

  // to be carefully, terminate with \0
  // there's no information in the reference whether the string is 0 terminated or not
  build_log[ret_val_size] = '\0';

  fprintf(stderr, "%s\n", build_log );


  return program;
}


int main(void)
{

  /* initialize random seed: */
    srand(time(NULL));

  printf("\n\n\n************************** STARTING TEST_ARRAY *******************************\n\n");

  // Fill stops_list_np with pass unique id
  unsigned int passId = 0;
  for (int i = 0; i < STOPS_NUM; ++i) {
    printf("Generating stop: %d\n" , i);
    stopsArrivalList[i].stopNum = i;
    stopsArrivalList[i].wIndex = 0;
    for (int j = 0; j < STOP_MAX_PASS; ++j) {
      stopsArrivalList[i].pass[j].passId = passId;
      stopsArrivalList[i].pass[j].origStop = i;
      stopsArrivalList[i].pass[j].destStop = STOPS_NUM - 1;
      //stopsArrivalList[i].pass[j].arrivalTime = rand() % PASS_TOTAL_ARRIVAL_TIME;
      stopsArrivalList[i].pass[j].arrivalTime = j/3;
      stopsArrivalList[i].pass[j].alightTime = 0;
      stopsArrivalList[i].pass[j].status = PASS_STATUS_TO_ARRIVE;
      stopsArrivalList[i].total ++;
      stopsArrivalList[i].lastEmtpy ++;
      passId ++;
    }
  }

#if PRINT_LIST
  for (int i = 0; i < STOPS_NUM; ++i) {
    printf("\nStop arrival list %d, total %d\n" ,
           stopsArrivalList[i].stopNum, stopsArrivalList[i].total);

    for (int j = 0; j < stopsArrivalList[i].total; ++j) {
      printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, status %d\n",
             stopsArrivalList[i].pass[j].passId,
             stopsArrivalList[i].pass[j].origStop,
             stopsArrivalList[i].pass[j].destStop,
             stopsArrivalList[i].pass[j].arrivalTime,
             stopsArrivalList[i].pass[j].alightTime,
             stopsArrivalList[i].pass[j].status);
    }
  }

  for (int i = 0; i < STOPS_NUM; ++i) {
    printf("\nStop queue list %d, total %d\n" ,
           stopsQueueList[i].stopNum, stopsQueueList[i].total);

    for (int j = 0; j < stopsQueueList[i].total; ++j) {
      printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, status %d\n",
             stopsQueueList[i].pass[j].passId,
             stopsQueueList[i].pass[j].origStop,
             stopsQueueList[i].pass[j].destStop,
             stopsQueueList[i].pass[j].arrivalTime,
             stopsQueueList[i].pass[j].alightTime,
             stopsQueueList[i].pass[j].status);
    }
  }
#endif


#if USE_OPENCL

  unsigned int devId = 0;
  unsigned int simTime = MAX_SIM_TIME;
  clock_t procTimeCL;
  size_t szGlobalWorkSize;        // 1D var for Total # of work items
  size_t szGlobalWorkSizeOne;        // 1D var for Total # of work items
  size_t szLocalWorkSize;       // 1D var for # of work items in the work group

  cl_int err;
  opencl_init(devId);

  // set and log Global and Local work size dimensions
  printf("Starting...\n\n# of elements (STOPS_NUM) \t= %i\n", STOPS_NUM);
  szLocalWorkSize = 1000;
  szGlobalWorkSize = shrRoundUp((int) szLocalWorkSize, STOPS_NUM); // rounded up to the nearest multiple of the LocalWorkSize
  printf(
      "Global Work Size \t\t= %u\nLocal Work Size \t\t= %u\n# of Work Groups \t\t= %u\n\n",
      szGlobalWorkSize,
      szLocalWorkSize,
      (szGlobalWorkSize % szLocalWorkSize + szGlobalWorkSize / szLocalWorkSize));

  // Build kernel program
  cl_program kernels = buildProgramFromFile(context, "kernels.c");
  test1 = clCreateKernel(kernels, "test1", &err);
  checkErr(err, __LINE__, "clCreateKernel (test1)");

  // Create the buffers
  cl_mem stopsArrivalListMemObj = clCreateBuffer(context, CL_MEM_READ_WRITE,
                                                 sizeof(SL_TYPE) * STOPS_NUM, NULL, &err );
  checkErr(err, __LINE__, "creating stopsArrivalListMemObj");
  cl_mem stopsQueueListMemObj = clCreateBuffer(context, CL_MEM_READ_WRITE,
                                                 sizeof(SL_TYPE) * STOPS_NUM, NULL, &err );
  checkErr(err, __LINE__, "creating stopsQueueListMemObj");



  // Copy the data to memory buffers
  err = clEnqueueWriteBuffer(command_queue, stopsArrivalListMemObj, CL_TRUE, 0,
                             sizeof(SL_TYPE) * STOPS_NUM,
                             stopsArrivalList, 0, NULL, NULL);
  checkErr( err,__LINE__, "clEnqueueWriteBuffer stopsArrivalListMemObj");
  err = clEnqueueWriteBuffer(command_queue, stopsQueueListMemObj, CL_TRUE, 0,
                             sizeof(SL_TYPE) * STOPS_NUM,
                             stopsQueueList, 0, NULL, NULL);
  checkErr( err,__LINE__, "clEnqueueWriteBuffer stopsArrivalListMemObj");


  // Set the arguments of the kernel
  err = clSetKernelArg(test1, 0, sizeof(cl_mem), (void *)&stopsArrivalListMemObj);
  checkErr( err,__LINE__, "clSetKernelArg stopsArrivalListMemObj");

  err = clSetKernelArg(test1, 1, sizeof(cl_mem), (void *)&stopsQueueListMemObj);
  checkErr( err,__LINE__, "clSetKernelArg stopsArrivalListMemObj");

  err = clSetKernelArg(test1, 2, sizeof(cl_uint), (void *)&simTime);
  checkErr( err,__LINE__, "clSetKernelArg simTime");


  // Running the kernel
  procTimeCL = clock();
  err = clEnqueueNDRangeKernel(command_queue, test1, 1, NULL,
                               &szGlobalWorkSize, &szLocalWorkSize, 0, NULL, NULL);


  clFinish(command_queue);

  procTimeCL = clock() - procTimeCL;
  checkErr(err,__LINE__,  "clEnqueueNDRangeKernel test1");



  // Read the buffer to host
  err = clEnqueueReadBuffer(command_queue, stopsArrivalListMemObj, CL_TRUE, 0,
                           sizeof(SL_TYPE) * STOPS_NUM,
                           stopsArrivalList, 0, NULL, NULL);
  checkErr(err,__LINE__,  "clEnqueueReadBuffer stopsArrivalListMemObj");

  err = clEnqueueReadBuffer(command_queue, stopsQueueListMemObj, CL_TRUE, 0,
                           sizeof(SL_TYPE) * STOPS_NUM,
                           stopsQueueList, 0, NULL, NULL);
  checkErr(err,__LINE__,  "clEnqueueReadBuffer stopsQueueListMemObj");



#endif

#if (USE_OPENCL == 0)
  clock_t procTimeC;
  procTimeC = clock();

  for (unsigned int simTime = 0; simTime < MAX_SIM_TIME; ++simTime) {

    for (unsigned int i = 0; i < STOPS_NUM; ++i) {
      while(1){
        // Check if the list is finished
        if(stopsArrivalList[i].wIndex >= STOP_MAX_PASS){
          break;
        }

        // Check pass status
        if(stopsArrivalList[i].pass[stopsArrivalList[i].wIndex].status != PASS_STATUS_TO_ARRIVE){
          break;
        }


        // Check arrival time
        if(simTime < stopsArrivalList[i].pass[stopsArrivalList[i].wIndex].arrivalTime){
          break;
        }


        memcpy(&stopsQueueList[i].pass[stopsQueueList[i].lastEmtpy],
          &stopsArrivalList[i].pass[stopsArrivalList[i].wIndex], sizeof(PASS_TYPE));

        stopsQueueList[i].pass[stopsQueueList[i].lastEmtpy].status = PASS_STATUS_ARRIVED;
        stopsQueueList[i].lastEmtpy ++;
        stopsQueueList[i].total ++;


        stopsArrivalList[i].pass[stopsArrivalList[i].wIndex].status = PASS_STATUS_EMPTY;
        stopsArrivalList[i].lastEmtpy ++;
        stopsArrivalList[i].total --;
        stopsArrivalList[i].wIndex ++;
      }
    }
  }
  procTimeC = clock() - procTimeC;
#endif


#if PRINT_LIST
  for (int i = 0; i < STOPS_NUM; ++i) {
    printf("\nPost stop %d, total %d, wIndex %d\n" ,
           stopsArrivalList[i].stopNum, stopsArrivalList[i].total, stopsArrivalList[i].wIndex);

    for (int j = 0; j < stopsArrivalList[i].total; ++j) {
      printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, status %d\n",
             stopsArrivalList[i].pass[j].passId,
             stopsArrivalList[i].pass[j].origStop,
             stopsArrivalList[i].pass[j].destStop,
             stopsArrivalList[i].pass[j].arrivalTime,
             stopsArrivalList[i].pass[j].alightTime,
             stopsArrivalList[i].pass[j].status);
    }

    for (int i = 0; i < STOPS_NUM; ++i) {
      printf("\nPost Stop queue list %d, total %d\n" ,
             stopsQueueList[i].stopNum, stopsQueueList[i].total);

      for (int j = 0; j < stopsQueueList[i].total; ++j) {
        printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, status %d\n",
               stopsQueueList[i].pass[j].passId,
               stopsQueueList[i].pass[j].origStop,
               stopsQueueList[i].pass[j].destStop,
               stopsQueueList[i].pass[j].arrivalTime,
               stopsQueueList[i].pass[j].alightTime,
               stopsQueueList[i].pass[j].status);
      }
    }
  }
#endif


#if USE_OPENCL
  printf("\nElapsed CL: %f seconds\n", (double)(procTimeCL) / CLOCKS_PER_SEC);
#else
  printf("\nElapsed C++: %f seconds\n", (double)(procTimeC) / CLOCKS_PER_SEC);
#endif

  return 0;

}
