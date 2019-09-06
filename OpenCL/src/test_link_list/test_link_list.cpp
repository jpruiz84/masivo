#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <string.h>
#include <oclUtils.h>
#include <shrQATest.h>

#include "linkList.h"
#include "mergeSort.h"

#define STOPS_NUM                    1
#define STOP_MAX_PASS               10
#define SIM_TIME                  6000     // In secs
#define PASS_TOTAL_ARRIVAL_TIME   3600     // In secs

#define PRINT_LIST      0


PASS_TYPE passList[STOPS_NUM * STOP_MAX_PASS];

SLS_TYPE stopsArrival[STOPS_NUM];
SLS_TYPE stopsQueue[STOPS_NUM];
SLS_TYPE stopsAlight[STOPS_NUM];



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
  clock_t procTime;

  printf("\fStarting test link list.\n");


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

  // Create memory buffers for the pass list
  cl_mem passListMemObj = clCreateBuffer(context, CL_MEM_READ_ONLY,
                                         STOPS_NUM * STOP_MAX_PASS * sizeof(PASS_TYPE),
                                         NULL, &ret);



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
      listInsert(&stopsArrival[i].listHt,
                 &passList[i * STOP_MAX_PASS + j].listEntry);
      stopsArrival[i].total ++;

      passId++;
    }
  }

#if PRINT_LIST
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsArrival[%d], head: %p, tail: %p\n",
           i, stopsArrival[i].listHt.head, stopsArrival[i].listHt.tail);
    listPrintPass(&stopsArrival[i].listHt);
  }
#endif

  // Sort all arrival list stops
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("Sorting arrival list from stop %d/%d\n", i, STOPS_NUM - 1);
    sortByArrivalTime(&stopsArrival[i].listHt);
  }



#if PRINT_LIST
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsArrival[%d], head: %p, tail: %p\n",
           i, stopsArrival[i].listHt.head, stopsArrival[i].listHt.tail);
    listPrintPass(&stopsArrival[i].listHt);
  }
#endif

#if 1
  // Copy the passList to memory buffers
  ret = clEnqueueWriteBuffer(command_queue, passListMemObj, CL_TRUE, 0,
                             STOPS_NUM * STOP_MAX_PASS * sizeof(PASS_TYPE),
                             passList, 0, NULL, NULL);

  printf("1 ret: %d\n", ret);
  // Create a program from the kernel source
  cl_program program = clCreateProgramWithSource(context, 1,
          (const char **)&source_str, (const size_t *)&source_size, &ret);

  // Build the program
  ret = clBuildProgram(program, 1, &device_id, NULL, NULL, NULL);

  printf("2 ret: %d\n", ret);
  print_build_log(program, device_id);


  // Create the OpenCL kernel
  cl_kernel kernel = clCreateKernel(program, "test1", &ret);


  // Set the arguments of the kernel
  ret = clSetKernelArg(kernel, 0, sizeof(cl_mem), (void *)&passListMemObj);

  // Execute the OpenCL kernel on the list
  size_t global_item_size = 1; // Process the entire lists
  size_t local_item_size = 1; // Divide work items into groups of 64

  ret = clEnqueueNDRangeKernel(command_queue, kernel, 1, NULL,
          &global_item_size, &local_item_size, 0, NULL, NULL);

  printf("3 ret: %d\n", ret);


   ret = clEnqueueReadBuffer(command_queue, passListMemObj, CL_TRUE, 0,
                             STOPS_NUM * STOP_MAX_PASS * sizeof(PASS_TYPE),
                             passList, 0, NULL, NULL);


   printf("4 ret: %d\n", ret);

#endif



#if 1

  procTime = clock();
  // Run the simulation
  for (unsigned int sim_time = 0; sim_time < SIM_TIME; ++sim_time) {
    if((sim_time % 100) == 0){
      printf("\rtime: %d   ", sim_time);

    }

    // For each stop
    for (unsigned int i = 0; i < STOPS_NUM; ++i) {

      if(stopsArrival[i].total > 0){

        while(sim_time == PASS_FROM_THIS(stopsArrival[i].listHt.head)->arrivalTime){

          listInsert(&stopsQueue[i].listHt, listPop(&stopsArrival[i].listHt));
          stopsArrival[i].total --;
          stopsQueue[i].total ++;

          if(stopsArrival[i].total == 0){
            break;
          }
        }
      }
    }
  }

  procTime = clock() - procTime;
#endif



#if PRINT_LIST
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsArrival[%d], head: %p, tail: %p\n",
           i, stopsArrival[i].listHt.head, stopsArrival[i].listHt.tail);

    listPrintPass(&stopsArrival[i].listHt);

  }


  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsQueue[%d], head: %p, tail: %p\n",
           i, stopsQueue[i].listHt.head, stopsQueue[i].listHt.tail);

    listPrintPass(&stopsQueue[i].listHt);
  }
#endif

  printf("\nElapsed: %f seconds\n", (double)(procTime) / CLOCKS_PER_SEC);

  return 0;
}
