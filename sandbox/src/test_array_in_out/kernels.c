#ifndef __OPENCL_VERSION__
#define __kernel
#define __global
#define __local
#endif

#define STOPS_NUM               3000
#define STOP_MAX_PASS           10000
#define PRINT_LIST              0


typedef unsigned int    uint32_t;

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



//    ___ _____ _   ___ _____ ___ _  _  ___     _  _____ ___ _  _ ___ _
//   / __|_   _/_\ | _ \_   _|_ _| \| |/ __|   | |/ / __| _ \ \| | __| |
//   \__ \ | |/ _ \|   / | |  | || .` | (_ |   | ' <| _||   / .` | _|| |__
//   |___/ |_/_/ \_\_|_\ |_| |___|_|\_|\___|   |_|\_\___|_|_\_|\_|___|____|
//

__kernel void test1(
    __global SL_TYPE* stopsArrivalList,
    __global SL_TYPE* stopsQueueList,
    unsigned int maxSimTime
    )
{
  int i = get_global_id(0);

  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (i >= STOPS_NUM){
    return;
  }

#if PRINT_LIST
  printf("\n\n************* START KERNEL *************************************\n");
  printf("maxSimTime: %d\n", maxSimTime);

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

  for (unsigned int simTime = 0; simTime < maxSimTime; ++simTime) {
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


      stopsQueueList[i].pass[stopsQueueList[i].lastEmtpy] =
          stopsArrivalList[i].pass[stopsArrivalList[i].wIndex];

      stopsQueueList[i].pass[stopsQueueList[i].lastEmtpy].status = PASS_STATUS_ARRIVED;
      stopsQueueList[i].lastEmtpy ++;
      stopsQueueList[i].total ++;


      stopsArrivalList[i].pass[stopsArrivalList[i].wIndex].status = PASS_STATUS_EMPTY;
      stopsArrivalList[i].lastEmtpy ++;
      stopsArrivalList[i].total --;
      stopsArrivalList[i].wIndex ++;
    }
  }



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

  printf("************* END KERNEL **************************************\n\n");
#endif




}
