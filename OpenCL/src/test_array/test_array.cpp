#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <string.h>
#include <oclUtils.h>
#include <shrQATest.h>

#define STOPS_NUM                    300
#define STOP_MAX_PASS                10000
#define MAX_SIM_TIME               6000     // In secs
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


#define MAX_SOURCE_SIZE (0x100000)

//////build log////////////
void print_build_log(cl_program program, cl_device_id dev) {
    size_t log_size;
    clGetProgramBuildInfo(program, dev, CL_PROGRAM_BUILD_LOG,
                          0, NULL, &log_size);
    char *log = (char *)malloc(log_size + 1);
    clGetProgramBuildInfo(program, dev, CL_PROGRAM_BUILD_LOG,
                          log_size, log, NULL);
    fprintf(stderr, "\n---------- BUILD LOG ----------\n%s\n", log);
    fprintf(stderr, "---------------------------------------\n");
    free(log);
}

int
main()
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
    printf("\nStop %d, total %d\n" ,
           stopsArrivalList[i].stopNum, stopsArrivalList[i].total);

    for (int j = 0; j < STOP_MAX_PASS; ++j) {
      printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, status %d\n",
             stopsArrivalList[i].pass[j].passId,
             stopsArrivalList[i].pass[j].origStop,
             stopsArrivalList[i].pass[j].destStop,
             stopsArrivalList[i].pass[j].arrivalTime,
             stopsArrivalList[i].pass[j].alightTime,
             stopsArrivalList[i].pass[j].status);
    }
  }
#endif


#if USE_OPENCL
  clock_t procTimeCL;
  size_t szGlobalWorkSize;        // 1D var for Total # of work items
  size_t szGlobalWorkSizeOne;        // 1D var for Total # of work items
  size_t szLocalWorkSize;       // 1D var for # of work items in the work group


  shrLog("Starting...\n\n# of elements (STOPS_NUM) \t= %i\n", STOPS_NUM);
  // set and log Global and Local work size dimensions
  szLocalWorkSize = 300;
  szGlobalWorkSize = shrRoundUp((int) szLocalWorkSize, STOPS_NUM); // rounded up to the nearest multiple of the LocalWorkSize
  shrLog(
      "Global Work Size \t\t= %u\nLocal Work Size \t\t= %u\n# of Work Groups \t\t= %u\n\n",
      szGlobalWorkSize,
      szLocalWorkSize,
      (szGlobalWorkSize % szLocalWorkSize + szGlobalWorkSize / szLocalWorkSize));



  // Load the kernel source code into the array source_str
  FILE *fp;
  char *source_str;
  size_t source_size;

  fp = fopen("src/test_array/kernels.c", "r");
  if (!fp) {
      fprintf(stderr, "Failed to load kernel.\n");
      exit(1);
  }
  source_str = (char*)malloc(MAX_SOURCE_SIZE);
  source_size = fread( source_str, 1, MAX_SOURCE_SIZE, fp);
  fclose( fp );


  // Get platform and device information
  cl_platform_id platform_id = NULL;
  cl_device_id device_id = NULL;
  cl_uint ret_num_devices;
  cl_uint ret_num_platforms;
  cl_int ret = clGetPlatformIDs(1, &platform_id, &ret_num_platforms);
  ret = clGetDeviceIDs(platform_id, CL_DEVICE_TYPE_DEFAULT, 1,
          &device_id, &ret_num_devices);

  // Create an OpenCL context
  cl_context context = clCreateContext( NULL, 1, &device_id, NULL, NULL, &ret);

  // Create a command queue
  cl_command_queue command_queue = clCreateCommandQueue(context, device_id, 0, &ret);

  printf("sizeof(stopsArrivalList): %zu\n", sizeof(SL_TYPE) * STOPS_NUM);

  // Create memory buffers for the pass list
  cl_mem stopsArrivalListMemObj = clCreateBuffer(context, CL_MEM_READ_WRITE,
                                                 sizeof(SL_TYPE) * STOPS_NUM,
                                         NULL, &ret);


  printf("1 ret: %d\n", ret);

  // Create a program from the kernel source
  cl_program program = clCreateProgramWithSource(context, 1,
          (const char **)&source_str, (const size_t *)&source_size, &ret);

  // Build the program
  ret = clBuildProgram(program, 1, &device_id, NULL, NULL, NULL);
  printf("2 ret: %d\n", ret);

  // Print build log
  print_build_log(program, device_id);


  // Create the OpenCL kernel
  cl_kernel kernel = clCreateKernel(program, "test1", &ret);
  printf("2a ret: %d\n", ret);



  // Copy the data to memory buffers
  ret = clEnqueueWriteBuffer(command_queue, stopsArrivalListMemObj, CL_TRUE, 0,
                             sizeof(SL_TYPE) * STOPS_NUM,
                             stopsArrivalList, 0, NULL, NULL);

  // Set the arguments of the kernel
  unsigned int simTime = MAX_SIM_TIME;
  ret = clSetKernelArg(kernel, 0, sizeof(cl_mem), (void *)&stopsArrivalListMemObj);
  printf("3a ret: %d\n", ret);


  ret = clSetKernelArg(kernel, 1, sizeof(cl_uint), (void *)&simTime);

  procTimeCL = clock();
  ret = clEnqueueNDRangeKernel(command_queue, kernel, 1, NULL,
                               &szGlobalWorkSize, &szLocalWorkSize, 0, NULL, NULL);


  clFinish(command_queue);

  procTimeCL = clock() - procTimeCL;

  printf("4 ret: %d\n", ret);


  ret = clEnqueueReadBuffer(command_queue, stopsArrivalListMemObj, CL_TRUE, 0,
                           sizeof(SL_TYPE) * STOPS_NUM,
                           stopsArrivalList, 0, NULL, NULL);

  printf("5 ret: %d\n", ret);

#endif

#if (USE_OPENCL == 0)
  clock_t procTimeC;
  procTimeC = clock();

  unsigned long iter = 0;

  for (int i = 0; i < STOPS_NUM; ++i) {

    stopsArrivalList[i].wIndex = 0;
    for (unsigned int simTime = 0; simTime < MAX_SIM_TIME; ++simTime) {

      while(1){
        if(simTime == stopsArrivalList[i].pass[stopsArrivalList[i].wIndex].arrivalTime){
          stopsArrivalList[i].pass[stopsArrivalList[i].wIndex].status = PASS_STATUS_ARRIVED;
          stopsArrivalList[i].wIndex ++;
          if(stopsArrivalList[i].wIndex >= stopsArrivalList[i].total){
            break;
          }
          iter ++;
        }else{
          break;
        }


      }
    }
  }
  procTimeC = clock() - procTimeC;
#endif


#if PRINT_LIST
  for (int i = 0; i < STOPS_NUM; ++i) {
    printf("\nPost stop %d, total %d, wIndex %d\n" ,
           stopsArrivalList[i].stopNum, stopsArrivalList[i].total, stopsArrivalList[i].wIndex);

    for (int j = 0; j < STOP_MAX_PASS; ++j) {
      printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, status %d\n",
             stopsArrivalList[i].pass[j].passId,
             stopsArrivalList[i].pass[j].origStop,
             stopsArrivalList[i].pass[j].destStop,
             stopsArrivalList[i].pass[j].arrivalTime,
             stopsArrivalList[i].pass[j].alightTime,
             stopsArrivalList[i].pass[j].status);
    }
  }
#endif


#if USE_OPENCL
  printf("\nElapsed CL: %f seconds\n", (double)(procTimeCL) / CLOCKS_PER_SEC);
#else
  printf("iter: %lu\n", iter);
  printf("\nElapsed C++: %f seconds\n", (double)(procTimeC) / CLOCKS_PER_SEC);
#endif

  return 0;
}
