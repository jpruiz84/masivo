#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <string.h>

#define STOPS_NUM                    3
#define STOP_MAX_PASS               10
#define SIM_TIME                  6000     // In secs
#define PASS_TOTAL_ARRIVAL_TIME   3600     // In secs

#define PRINT_LIST      0

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
}__attribute__ ((packed))
PASS_TYPE;

#define PASS_FROM_THIS(a) BASE_CR (a, PASS_TYPE, listEntry)

typedef struct {
  unsigned int total;
  LIST_HT listHt;
}__attribute__ ((packed))
SLS_TYPE;

int
listInit(
  LIST_HT *listHt
  )
{
  if(!listHt)
    return -1;

  listHt->head = NULL;
  listHt->tail = NULL;
  return 0;
}

int
listInsert(
  LIST_HT *listHt,
  LIST_ENTRY *entry
  )
{
  if(!listHt || !entry)
    return -1;

  if(!listHt->head){
    listHt->head = entry;
    listHt->tail = entry;
    entry->next = NULL;
    return 0;
  }

  listHt->tail->next = entry;
  listHt->tail = entry;
  entry->next = NULL;
  return 0;
}

int
listIsEmpty(
  LIST_HT *listHt
  )
{
  return (listHt->tail == NULL);
}

LIST_ENTRY*
listGetFirstNode(
  LIST_HT *listHt
  )
{
  return listHt->head;
}

LIST_ENTRY*
listGetNextNode(
  LIST_ENTRY *Node
  )
{
  return Node->next;
}

int
listIsTheLast(
  LIST_ENTRY *Node
  )
{
  return(Node->next == NULL);
}


int
swap(
  LIST_ENTRY *nodeA,
  LIST_ENTRY *nodeB
  )
{
  PASS_TYPE passTemp;

  memcpy(&passTemp, PASS_FROM_THIS(nodeA),
    sizeof(PASS_TYPE) - sizeof(LIST_ENTRY));

  memcpy(PASS_FROM_THIS(nodeA), PASS_FROM_THIS(nodeB),
    sizeof(PASS_TYPE) - sizeof(LIST_ENTRY));

  memcpy(PASS_FROM_THIS(nodeB), &passTemp,
    sizeof(PASS_TYPE) - sizeof(LIST_ENTRY));

  return 0;
}



int
listSortByArrivalTime(
  LIST_HT *listHt
  )
{
    int swapped;
  int i;
  LIST_ENTRY *ptr1;
  LIST_ENTRY *lptr = NULL;

  if(listHt == NULL){
    return -1;
  }

  do{
    swapped = 0;
    ptr1 = listHt->head;

    while(ptr1->next != lptr){
      if(PASS_FROM_THIS(ptr1)->arrivalTime > PASS_FROM_THIS(ptr1->next)->arrivalTime){
        swap(ptr1, ptr1->next);
        swapped = 1;
      }
      ptr1 = ptr1->next;
    }
    lptr = ptr1;
  }
  while(swapped);
}



PASS_TYPE passList[STOPS_NUM * STOP_MAX_PASS];

SLS_TYPE stopsArrival[STOPS_NUM];
SLS_TYPE stopsQueue[STOPS_NUM];
SLS_TYPE stopsAlight[STOPS_NUM];

int
main()
{
  LIST_ENTRY *node;
  PASS_TYPE *passEntry = NULL;

  printf("\fStarting test link list.\n");

  /* initialize random seed: */
  srand(time(NULL));

  for(unsigned int i = 0; i < STOPS_NUM; i++){
    listInit(&stopsArrival[i].listHt);
    listInit(&stopsQueue[i].listHt);
    listInit(&stopsAlight[i].listHt);
  }

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

  printf("passId: %d\n", passId);

#if PRINT_LIST
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsArrival[%d], head: 0x%08X, tail: head: 0x%08X\n",
           i, stopsArrival[i].listHt.head, stopsArrival[i].listHt.tail);

    if(listIsEmpty (&stopsArrival[i].listHt)){
      break;
    }

    node = listGetFirstNode(&stopsArrival[i].listHt);
    do {
      passEntry = PASS_FROM_THIS(node);
      printf("Stop %d, passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, next: %d\n",
        i, passEntry->passId, passEntry->origStop, passEntry->destStop,
        passEntry->arrivalTime, passEntry->alightTime, passEntry->listEntry.next);

      node = listGetNextNode(node);

    }while(node);
  }
#endif

  // Sort all arrival list stops
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("Sorting arrival list from stop %d/%d\n", i, STOPS_NUM - 1);
    listSortByArrivalTime(&stopsArrival[i].listHt);
  }



#if PRINT_LIST
  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsArrival[%d], head: 0x%08X, tail: head: 0x%08X\n",
           i, stopsArrival[i].listHt.head, stopsArrival[i].listHt.tail);

    if(listIsEmpty (&stopsArrival[i].listHt)){
      break;
    }

    node = listGetFirstNode(&stopsArrival[i].listHt);
    do {
      passEntry = PASS_FROM_THIS(node);
      printf("Stop %d, passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, next: %d\n",
        i, passEntry->passId, passEntry->origStop, passEntry->destStop,
        passEntry->arrivalTime, passEntry->alightTime, passEntry->listEntry.next);

      node = listGetNextNode(node);

    }while(node);
  }
#endif

  return 0;
}
