#ifndef __OPENCL_VERSION__
#define __kernel
#define __global
#endif

#define STOPS_NUM               300
#define STOP_MAX_PASS           10000
#define PRINT_LIST              0

#define EMPTY_LIST   (unsigned int)4294967295
#define END_LIST     (unsigned int)4294967295


typedef unsigned int    uint32_t;

#define NULL 0
#define BASE_CR(Record, TYPE, Field)  ((TYPE *) ((char *) (Record) - (char *) &(((TYPE *) 0)->Field)))


typedef struct _LIST_ENTRY LIST_ENTRY;
struct _LIST_ENTRY
{
  unsigned int next;
};

typedef struct {
  unsigned int head;
  unsigned int tail;
}
LIST_HT;

typedef struct {
  unsigned int passId;
  unsigned short origStop;
  unsigned short destStop;
  unsigned short arrivalTime;
  unsigned short alightTime;
  LIST_ENTRY listEntry;
}
PASS_TYPE;


typedef struct {
  unsigned int total;
  LIST_HT listHt;
}
SLS_TYPE;


int
listInsert(
  __global PASS_TYPE *pl,
  __global LIST_HT *listHt,
  unsigned int entry
  )
{

  if(listHt->head == EMPTY_LIST){
    listHt->head = entry;
    listHt->tail = entry;
    pl[entry].listEntry.next = END_LIST;
    return 0;
  }

  pl[listHt->tail].listEntry.next = entry;
  listHt->tail = entry;
  pl[entry].listEntry.next = END_LIST;
  return 0;
}

int
listIsEmpty(
  __global LIST_HT *listHt
  )
{
  return (listHt->tail == EMPTY_LIST || listHt->head == EMPTY_LIST);
}

unsigned int
listGetFirstNode(
  __global LIST_HT *listHt
  )
{
  return listHt->head;
}

unsigned int
listGetNextNode(
  __global PASS_TYPE *pl,
  unsigned int node
  )
{
  return pl[node].listEntry.next;
}

int
listIsTheLast(
  __global PASS_TYPE *pl,
  unsigned int node
  )
{

  return(pl[node].listEntry.next == END_LIST);
}

unsigned int
listPop(
  __global PASS_TYPE *pl,
  __global LIST_HT *listHt
  )
{

  unsigned int popEntry;

  popEntry = listHt->head;
  listHt->head = pl[listHt->head].listEntry.next;

  return popEntry;
}

int
listUpdateTail(
  __global PASS_TYPE *pl,
  __global LIST_HT *listHt
  )
{
  unsigned int cur = listHt->head;


  while(pl[cur].listEntry.next != END_LIST){
    cur = pl[cur].listEntry.next;
  }

  listHt->tail = cur;


  return 0;
}

int
listPrintPass(
  __global PASS_TYPE *pl,
  __global LIST_HT *listHt
  )
{

  unsigned int node;
  __global PASS_TYPE *passEntry = NULL;

  if(listIsEmpty (listHt)){
    return -1;
  }

  node = listGetFirstNode(listHt);
  do {
    passEntry = &pl[node];
    printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, cur: %d, next: %d\n",
      passEntry->passId, passEntry->origStop, passEntry->destStop,
      passEntry->arrivalTime, passEntry->alightTime,node, passEntry->listEntry.next);

    node = listGetNextNode(pl, node);

  }while(node != EMPTY_LIST);

  return 0;
}


typedef struct {
  PASS_TYPE  passList[STOPS_NUM * STOP_MAX_PASS];
  SLS_TYPE   stopsArrival[STOPS_NUM];
  SLS_TYPE   stopsQueue[STOPS_NUM];
  SLS_TYPE   stopsAlight[STOPS_NUM];
  uint32_t   simTime;
  uint32_t   cMaxSimTime;
}__attribute__ ((packed))
SIMULATION_DATA;



//    ___ _____ _   ___ _____ ___ _  _  ___     _  _____ ___ _  _ ___ _
//   / __|_   _/_\ | _ \_   _|_ _| \| |/ __|   | |/ / __| _ \ \| | __| |
//   \__ \ | |/ _ \|   / | |  | || .` | (_ |   | ' <| _||   / .` | _|| |__
//   |___/ |_/_/ \_\_|_\ |_| |___|_|\_|\___|   |_|\_\___|_|_\_|\_|___|____|
//

__kernel void movePass(
    __global SIMULATION_DATA *data,
    unsigned int simTime
    )
{
  int gid = get_global_id(0);

#if PRINT_LIST
  printf("\n\n************* START KERNEL *************************************\n");


  printf("data: %p\n", data);
  printf("sizeof(SIMULATION_DATA): %d\n", sizeof(SIMULATION_DATA));
  printf("data->stopsArrival[0].listHt.head: %d\n", data->stopsArrival[0].listHt.head);
  printf("data->stopsArrival[0].listHt.tail: %d\n", data->stopsArrival[0].listHt.tail);
  printf("data->passList[0].passId: %d\n", data->passList[0].passId);
  printf("&data->passList[0].passId: %p\n", &data->passList[0].passId);
  printf("data->passList[1].passId: %d\n", data->passList[1].passId);




  printf("simTime %d/%d, %d\n", simTime, data->cMaxSimTime, data->simTime);

  printf("org stopsArrival[%d], total: %d head %d, tail %d\n",
    gid, data->stopsArrival[gid].total, data->stopsArrival[gid].listHt.head,
    data->stopsArrival[gid].listHt.tail);
  listPrintPass(data->passList, &data->stopsArrival[gid].listHt);
  printf("org stopsQueue[%d], total: %d head %d, tail %d\n",
    gid, data->stopsQueue[gid].total, data->stopsQueue[gid].listHt.head,
    data->stopsQueue[gid].listHt.tail);
  listPrintPass(data->passList, &data->stopsQueue[gid].listHt);

#endif

  if(data->stopsArrival[gid].total > 0){
    while(data->simTime == data->passList[data->stopsArrival[gid].listHt.head].arrivalTime){
      listInsert(data->passList, &data->stopsQueue[gid].listHt,
                 listPop(data->passList, &data->stopsArrival[gid].listHt));
      data->stopsArrival[gid].total--;
      data->stopsQueue[gid].total++;

      if(data->stopsArrival[gid].total == 0){
        break;
      }
    }
  }


#if PRINT_LIST
  printf("post stopsArrival[%d], total: %d head %d, tail %d\n",
    gid, data->stopsArrival[gid].total, data->stopsArrival[gid].listHt.head,
    data->stopsArrival[gid].listHt.tail);
  listPrintPass(data->passList, &data->stopsArrival[gid].listHt);

  printf("post stopsQueue[%d], total: %d head %d, tail %d\n",
    gid, data->stopsQueue[gid].total, data->stopsQueue[gid].listHt.head,
    data->stopsQueue[gid].listHt.tail);
  listPrintPass(data->passList, &data->stopsQueue[gid].listHt);
  printf("************* END KERNEL **************************************\n\n");
#endif


}


__kernel void updateSim(
    __global SIMULATION_DATA *data,
    unsigned int simTime
    )
{
  int gid = get_global_id(0);
  //printf("\n\n************* START KERNEL UPDATE SIM ***************************\n");
  data->simTime ++;
  //printf("simTime updated to: %d\n", data->simTime);
  //printf("\n\n************* END KERNEL UPDATE SIM ***************************\n");


}
