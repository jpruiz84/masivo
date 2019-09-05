#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <string.h>

#include "linkList.h"
#include "mergeSort.h"

#define STOPS_NUM                    300
#define STOP_MAX_PASS               10000
#define SIM_TIME                  6000     // In secs
#define PASS_TOTAL_ARRIVAL_TIME   3600     // In secs

#define PRINT_LIST      0


PASS_TYPE passList[STOPS_NUM * STOP_MAX_PASS];

SLS_TYPE stopsArrival[STOPS_NUM];
SLS_TYPE stopsQueue[STOPS_NUM];
SLS_TYPE stopsAlight[STOPS_NUM];

int
main()
{
  LIST_ENTRY *node;
  PASS_TYPE *passEntry = NULL;
  clock_t procTime;

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
    listBubleSortByArrivalTime(&stopsArrival[i].listHt);
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




#if 1

  procTime = clock();

  for (unsigned int sim_time = 0; sim_time < SIM_TIME; ++sim_time) {
    if((sim_time % 1) == 0){
      printf("\rtime: %d", sim_time);

    }

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

  for (unsigned int i = 0; i < STOPS_NUM; ++i) {
    printf("\nstopsQueue[%d], head: 0x%08X, tail: head: 0x%08X\n",
           i, stopsQueue[i].listHt.head, stopsQueue[i].listHt.tail);

    if(listIsEmpty (&stopsQueue[i].listHt)){
      break;
    }

    node = listGetFirstNode(&stopsQueue[i].listHt);
    do {
      passEntry = PASS_FROM_THIS(node);
      printf("Stop %d, passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, next: %d\n",
        i, passEntry->passId, passEntry->origStop, passEntry->destStop,
        passEntry->arrivalTime, passEntry->alightTime, passEntry->listEntry.next);

      node = listGetNextNode(node);

    }while(node);
  }
#endif

  printf("Elapsed: %f seconds\n", (double)(procTime) / CLOCKS_PER_SEC);

  return 0;
}
