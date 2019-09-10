#ifndef __OPENCL_VERSION__
#define __kernel
#define __global
#endif

#define STOPS_NUM               300
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
    unsigned int simTime
    )
{
  int i = get_global_id(0);

  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (i >= STOPS_NUM){
    return;
  }

#if PRINT_LIST
  printf("\n\n************* START KERNEL *************************************\n");
  printf("simTime: %d\n", simTime);

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
#endif

  stopsArrivalList[i].wIndex = 0;
  for (unsigned iSimTime = 0; iSimTime < simTime; ++iSimTime) {
    while(1){
      if(simTime == stopsArrivalList[i].pass[stopsArrivalList[i].wIndex].arrivalTime){
        stopsArrivalList[i].pass[stopsArrivalList[i].wIndex].status = PASS_STATUS_ARRIVED;
        stopsArrivalList[i].wIndex ++;
        if(stopsArrivalList[i].wIndex >= stopsArrivalList[i].total){
          break;
        }
      }else{
        break;
      }
    }
  }



#if PRINT_LIST
  printf("\nPost stop %d, total %d\n" ,
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

  printf("************* END KERNEL **************************************\n\n");
#endif




}
