#ifndef __OPENCL_VERSION__
#define __kernel
#define __global
#endif


#define NULL 0
#define BASE_CR(Record, TYPE, Field)  ((TYPE *) ((char *) (Record) - (char *) &(((TYPE *) 0)->Field)))


typedef struct _LIST_ENTRY LIST_ENTRY;
struct _LIST_ENTRY
{
  LIST_ENTRY *next;
} __attribute__ ((packed));

typedef struct {
  LIST_ENTRY *head;
  LIST_ENTRY *tail;
}__attribute__ ((packed))
LIST_HT;

typedef struct {
  unsigned int passId;
  unsigned short origStop;
  unsigned short destStop;
  unsigned short arrivalTime;
  unsigned short alightTime;
  LIST_ENTRY listEntry;
}__attribute__ ((packed)) PASS_TYPE;

typedef struct {
  unsigned int total;
  LIST_HT listHt;
}__attribute__ ((packed))
SLS_TYPE;

#define PASS_FROM_THIS(a) BASE_CR (a, PASS_TYPE, listEntry)


int
listIsEmpty(
  __global LIST_HT *listHt
  )
{
  return (listHt->tail == NULL || listHt->head == NULL);
}


LIST_ENTRY*
listPop(
  __global LIST_HT *listHt,
  unsigned long offsetAddr
  )
{
  LIST_ENTRY* popEntry;
  LIST_ENTRY* returnEntry;

  returnEntry = listHt->head;
  popEntry = (LIST_ENTRY*)((unsigned long)listHt->head + offsetAddr);
  listHt->head = popEntry->next;

  return returnEntry;
}

int
listInsert(
  __global LIST_HT *listHt,
  LIST_ENTRY *entry,
  unsigned long offsetAddr
  )
{
  LIST_ENTRY* tailEntry;
  LIST_ENTRY* entryFull;

  entryFull = (LIST_ENTRY*)((unsigned long)entry + offsetAddr);

  // If empty
  if(!listHt->head){
    listHt->head = entry;
    listHt->tail = entry;
    entryFull->next = NULL;
    return 0;
  }

  tailEntry = (LIST_ENTRY*)((unsigned long)listHt->tail+ offsetAddr);

  tailEntry->next = entry;
  listHt->tail = entry;
  entryFull->next = NULL;
  return 0;
}

LIST_ENTRY*
listGetFirstNode(
  __global LIST_HT *listHt,
  unsigned long offsetAddr
  )
{
  return (LIST_ENTRY*)((unsigned long)listHt->head + offsetAddr);
}

LIST_ENTRY*
listGetNextNode(
  LIST_ENTRY *Node,
  unsigned long offsetAddr
  )
{
  return (LIST_ENTRY*)((unsigned long)Node->next + offsetAddr);
}

int
listPrintPass(
  __global LIST_HT *listHt,
  unsigned long offsetAddr
  )
{

  LIST_ENTRY *node;
  PASS_TYPE *passEntry = NULL;

  if(listIsEmpty (listHt)){
    return -1;
  }

  node = listGetFirstNode(listHt, offsetAddr);
  while(1){
    passEntry = PASS_FROM_THIS(node);
    printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, cur: %p, next: %p\n",
      passEntry->passId, passEntry->origStop, passEntry->destStop,
      passEntry->arrivalTime, passEntry->alightTime, &passEntry->listEntry, passEntry->listEntry.next);

    if(!node->next){
      break;
    }
    node = listGetNextNode(node, offsetAddr);
  }

  return 0;
}


__kernel void movePass(
    __global PASS_TYPE *passList,
    __global SLS_TYPE *stopsArrival,
    __global SLS_TYPE *stopsQueue,
    unsigned int simTime,
    unsigned long offsetHost
    )
{
  int gid = get_global_id(0);
  unsigned long offsetDev = (unsigned long)passList;
  unsigned long offsetAddr = offsetDev - offsetHost;


#if 0
  printf("\n\n************* START KERNEL *************************************\n");
  printf("stopsArrival[gid].total: %d\n", stopsArrival[gid].total);
  printf("stopsArrival[gid].listHt.head: %p\n", stopsArrival[gid].listHt.head);
  printf("head addr: %p\n", (unsigned long)stopsArrival[gid].listHt.head + offsetAddr);
  printf("org stopsArrival\n");
  listPrintPass(&stopsArrival[gid].listHt, offsetAddr);
  printf("org stopsQueue, head %p, tail %p\n", stopsQueue[gid].listHt.head, stopsQueue[gid].listHt.tail);
  listPrintPass(&stopsQueue[gid].listHt, offsetAddr);
  printf("simTime: %d\n", simTime);
#endif


  if(stopsArrival[gid].total > 0){

    while(simTime == PASS_FROM_THIS((unsigned long)stopsArrival[gid].listHt.head + offsetAddr)->arrivalTime){
      listInsert(&stopsQueue[gid].listHt, listPop(&stopsArrival[gid].listHt, offsetAddr), offsetAddr);
      stopsArrival[gid].total--;
      stopsQueue[gid].total++;

      if(stopsArrival[gid].total == 0){
        break;
      }
    }
  }

#if 0

  printf("\n\npost stopsArrival\n");
  listPrintPass(&stopsArrival[gid].listHt, offsetAddr);

  printf("post stopsQueue, head %p, tail %p\n", stopsQueue[gid].listHt.head, stopsQueue[gid].listHt.tail);
  listPrintPass(&stopsQueue[gid].listHt, offsetAddr);
  printf("************* END KERNEL **************************************\n\n");
#endif

}

__kernel void test3(
    __global PASS_TYPE *passList,
    __global SLS_TYPE *stopsArrival,
    __global SLS_TYPE *stopsQueue,
    unsigned int simTime,
    unsigned long offsetHost
    )
{
  int gid = get_global_id(0);
  unsigned long offsetDev = (unsigned long)passList;



  printf("\n\nSTART KERNEL *************************************\n");
  printf("offsetDev: %p\n", offsetDev);
  printf("offsetHost: %p\n", offsetHost);

  unsigned long offsetAddr = offsetDev - offsetHost;
  printf("offsetAddr: %p\n", offsetAddr);



  printf("stopsArrival[gid].total: %d\n", stopsArrival[gid].total);

  printf("stopsArrival[gid].listHt.head: %p\n", stopsArrival[gid].listHt.head);


  printf("head addr: %p\n", (unsigned long)stopsArrival[gid].listHt.head + offsetAddr);

  printf("org stopsArrival\n");
  listPrintPass(&stopsArrival[gid].listHt, offsetAddr);
  printf("org stopsQueue, head %p, tail %p\n", stopsQueue[gid].listHt.head, stopsQueue[gid].listHt.tail);
  listPrintPass(&stopsQueue[gid].listHt, offsetAddr);


  listInsert(&stopsQueue[gid].listHt,
    listPop(&stopsArrival[gid].listHt, offsetAddr), offsetAddr);

  listInsert(&stopsQueue[gid].listHt,
    listPop(&stopsArrival[gid].listHt, offsetAddr), offsetAddr);

  listInsert(&stopsQueue[gid].listHt,
    listPop(&stopsArrival[gid].listHt, offsetAddr), offsetAddr);


  printf("\n\npost stopsArrival\n");
  listPrintPass(&stopsArrival[gid].listHt, offsetAddr);

  printf("post stopsQueue, head %p, tail %p\n", stopsQueue[gid].listHt.head, stopsQueue[gid].listHt.tail);
  listPrintPass(&stopsQueue[gid].listHt, offsetAddr);





  printf("END KERNEL **************************************\n\n");

}


__kernel void test2(
    __global PASS_TYPE *passList,
    __global SLS_TYPE *stopsArrival,
    __global SLS_TYPE *stopsQueue,
    unsigned int simTime,
    unsigned long offsetHost
    )
{
  int gid = get_global_id(0);
  unsigned long offsetDev = (unsigned long)passList;



  printf("\n\nSTART KERNEL *************************************\n");
  printf("offsetDev: %p\n", offsetDev);
  printf("offsetHost: %p\n", offsetHost);

  unsigned long offsetAddr = offsetDev - offsetHost;
  printf("offsetAddr: %p\n", offsetAddr);



  printf("stopsArrival[gid].total: %d\n", stopsArrival[gid].total);

  printf("stopsArrival[gid].listHt.head: %p\n", stopsArrival[gid].listHt.head);


  printf("head addr: %p\n", (unsigned long)stopsArrival[gid].listHt.head + offsetAddr);

  printf("head: paddId %d, arrivalTime %d, addr: %p, next: %p\n",
    PASS_FROM_THIS((unsigned long)stopsArrival[gid].listHt.head + offsetAddr)->passId,
    PASS_FROM_THIS((unsigned long)stopsArrival[gid].listHt.head + offsetAddr)->arrivalTime,
    &PASS_FROM_THIS((unsigned long)stopsArrival[gid].listHt.head + offsetAddr)->listEntry,
    PASS_FROM_THIS((unsigned long)stopsArrival[gid].listHt.head + offsetAddr)->listEntry.next);


  for (int i = 0; i < stopsArrival[gid].total; ++i) {
    printf("(%d) paddId %d, arrivalTime %d, addr: %p, next: %p\n",
      i, passList[i].passId, passList[i].arrivalTime, &passList[i].listEntry, passList[i].listEntry.next);

  }



  printf("END KERNEL **************************************\n\n");

}


__kernel void test1(
    __global PASS_TYPE *passList
    )
{
  int gid = get_global_id(0);

  int i = 0;

  printf("(%d) paddId %d, arrivalTime %d\n", i, passList[i].passId, passList[i].arrivalTime);
  passList[i].passId = 8484;
  printf("(%d) paddId %d, arrivalTime %d\n", i, passList[i].passId, passList[i].arrivalTime);

}

