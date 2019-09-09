#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <string.h>
#include <oclUtils.h>
#include <shrQATest.h>

#include "linkList.h"
#include "mergeSort.h"

#define STOPS_NUM                    1
#define STOP_MAX_PASS                10
#define MAX_SIM_TIME               6000     // In secs
#define PASS_TOTAL_ARRIVAL_TIME    3600     // In secs
#define PRINT_LIST      0
#define USE_OPENCL      1

typedef struct {
  PASS_TYPE  passList[STOPS_NUM * STOP_MAX_PASS];
  SLS_TYPE   stopsArrival[STOPS_NUM];
  SLS_TYPE   stopsQueue[STOPS_NUM];
  SLS_TYPE   stopsAlight[STOPS_NUM];
  uint32_t   simTime;
  uint32_t   cMaxSimTime;
}__attribute__ ((packed))
SIMULATION_DATA;

SIMULATION_DATA data;
PASS_TYPE* passList;
SLS_TYPE* stopsArrival;
SLS_TYPE* stopsQueue;
SLS_TYPE* stopsAlight;


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



  printf("\fStarting test link list.\n");

  passList = data.passList;
  stopsArrival = data.stopsArrival;
  stopsQueue = data.stopsQueue;
  stopsAlight = data.stopsAlight;


  /* initialize random seed: */
  srand(time(NULL));

  // Init stop lists
  for(unsigned int i = 0; i < STOPS_NUM; i++){
    listInit(&stopsArrival[i].listHt);
    listInit(&stopsQueue[i].listHt);
    listInit(&stopsAlight[i].listHt);
  }
  // Filling the stops arrival list with random pass arrival time
  unsigned int passId = 0;
  for(unsigned int i = 0; i < STOPS_NUM; i++){
    for(unsigned int j = 0; j < STOP_MAX_PASS; j++){
      passList[i * STOP_MAX_PASS + j].passId = passId;
      passList[i * STOP_MAX_PASS + j].origStop = i;
      passList[i * STOP_MAX_PASS + j].destStop = STOPS_NUM - 1;
      passList[i * STOP_MAX_PASS + j].arrivalTime =
          rand() % PASS_TOTAL_ARRIVAL_TIME;
      passList[i * STOP_MAX_PASS + j].alightTime = 0;
      listInsert(passList, &stopsArrival[i].listHt,
                 i * STOP_MAX_PASS + j);
      stopsArrival[i].total ++;

      passId++;
    }
  }


#if PRINT_LIST
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsArrival[%d], total: %d, head: %d, tail: %d\n",
           i, stopsArrival[i].total, stopsArrival[i].listHt.head, stopsArrival[i].listHt.tail);
    listPrintPass(passList, &stopsArrival[i].listHt);

  }
#endif

  // Sort all arrival list stops
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("Sorting arrival list from stop %d/%d\n", i, STOPS_NUM - 1);
    sortByArrivalTime(passList, &stopsArrival[i].listHt);
  }



#if PRINT_LIST
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsArrival[%d], total: %d, head: %d, tail: %d\n",
           i, stopsArrival[i].total, stopsArrival[i].listHt.head, stopsArrival[i].listHt.tail);
    listPrintPass(passList, &stopsArrival[i].listHt);
  }
#endif



#if USE_OPENCL
  clock_t procTimeCL;
  size_t szGlobalWorkSize;        // 1D var for Total # of work items
  size_t szLocalWorkSize;       // 1D var for # of work items in the work group

  data.simTime = 0;
  data.cMaxSimTime = MAX_SIM_TIME;

  shrLog("Starting...\n\n# of elements (STOPS_NUM) \t= %i\n", STOPS_NUM);
  // set and log Global and Local work size dimensions
  szLocalWorkSize = 1;
  szGlobalWorkSize = shrRoundUp((int)szLocalWorkSize, STOPS_NUM);  // rounded up to the nearest multiple of the LocalWorkSize
  printf("Global Work Size \t\t= %zu\nLocal Work Size \t\t= %zu\n# of Work Groups \t\t= %zu\n\n",
         szGlobalWorkSize, szLocalWorkSize, (szGlobalWorkSize % szLocalWorkSize + szGlobalWorkSize/szLocalWorkSize));



  // Load the kernel source code into the array source_str
  FILE *fp;
  char *source_str;
  size_t source_size;

  fp = fopen("src/test_link_list/kernels.c", "r");
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

  printf("sizeof(data): %zu\n", sizeof(data));
  printf("sizeof(SIMULATION_DATA): %zu\n", sizeof(SIMULATION_DATA));
  printf("sizeof(data.passList): %zu\n", sizeof(data.passList));
  printf("sizeof(data.stopsArrival): %zu\n", sizeof(data.stopsArrival));

  // Create memory buffers for the pass list
  cl_mem dataMemObj = clCreateBuffer(context, CL_MEM_READ_WRITE,
                                         sizeof(SIMULATION_DATA),
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
  cl_kernel kernel = clCreateKernel(program, "movePass", &ret);

  // Copy the data to memory buffers
  ret = clEnqueueWriteBuffer(command_queue, dataMemObj, CL_TRUE, 0,
                             sizeof(SIMULATION_DATA),
                             &data, 0, NULL, NULL);

  // Set the arguments of the kernel
  ret = clSetKernelArg(kernel, 0, sizeof(cl_mem), (void *)&dataMemObj);

  szLocalWorkSize = 1;
  szGlobalWorkSize = STOPS_NUM;

  procTimeCL = clock();
  for (unsigned int simTime = 0; simTime < MAX_SIM_TIME; ++simTime) {
    ret = clSetKernelArg(kernel, 1, sizeof(cl_uint), (void *)&simTime);
    ret = clEnqueueNDRangeKernel(command_queue, kernel, 1, NULL,
                                 &szGlobalWorkSize, &szLocalWorkSize, 0, NULL, NULL);

  }
  procTimeCL = clock() - procTimeCL;


  printf("3 ret: %d\n", ret);


   ret = clEnqueueReadBuffer(command_queue, dataMemObj, CL_TRUE, 0,
                             sizeof(SIMULATION_DATA),
                             &data, 0, NULL, NULL);


   printf("4 ret: %d\n", ret);

#endif



#if (USE_OPENCL == 0)

   clock_t procTimeC;
   procTimeC = clock();
  // Run the simulation
  for (unsigned int simTime = 0; simTime < MAX_SIM_TIME; ++simTime) {
    if((simTime % 100) == 0){
      printf("\rtime: %d   ", simTime);

    }
    // For each stop
    for (unsigned int i = 0; i < STOPS_NUM; ++i) {

      if(stopsArrival[i].total > 0){
        while(simTime == passList[stopsArrival[i].listHt.head].arrivalTime){
          listInsert(passList, &stopsQueue[i].listHt, listPop(passList, &stopsArrival[i].listHt));
          stopsArrival[i].total --;
          stopsQueue[i].total ++;

          if(stopsArrival[i].total == 0){
            break;
          }
        }
      }
    }
  }

  procTimeC = clock() - procTimeC;

#endif



#if PRINT_LIST
  printf("\n\nAFTER SIMULATION\n");
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsArrival[%d], total: %d, head: %d, tail: %d\n",
           i, stopsArrival[i].total, stopsArrival[i].listHt.head, stopsArrival[i].listHt.tail);

    listPrintPass(passList, &stopsArrival[i].listHt);

  }


  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsQueue[%d], total: %d, head: %d, tail: %d\n",
           i, stopsQueue[i].total, stopsQueue[i].listHt.head, stopsQueue[i].listHt.tail);

    listPrintPass(passList, &stopsQueue[i].listHt);
  }
#endif

  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("stopsArrival[%d], total: %d, head: %d, tail: %d\n",
           i, stopsArrival[i].total, stopsArrival[i].listHt.head, stopsArrival[i].listHt.tail);

  }


  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("stopsQueue[%d], total: %d, head: %d, tail: %d\n",
           i, stopsQueue[i].total, stopsQueue[i].listHt.head, stopsQueue[i].listHt.tail);

  }

  //printf("\nElapsed C++: %f seconds\n", (double)(procTimeC) / CLOCKS_PER_SEC);
  printf("\nElapsed CL: %f seconds\n", (double)(procTimeCL) / CLOCKS_PER_SEC);


  return 0;
}
