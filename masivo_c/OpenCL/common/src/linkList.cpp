#include "linkList.h"


int
listInit(
  LIST_HT *listHt
  )
{
  if(!listHt)
    return -1;

  listHt->head = EMPTY_LIST;
  listHt->tail = EMPTY_LIST;
  return 0;
}

int
listInsert(
  PASS_TYPE *pl,
  LIST_HT *listHt,
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
  LIST_HT *listHt
  )
{
  return (listHt->tail == EMPTY_LIST || listHt->head == EMPTY_LIST);
}

unsigned int
listGetFirstNode(
  LIST_HT *listHt
  )
{
  return listHt->head;
}

unsigned int
listGetNextNode(
  PASS_TYPE *pl,
  unsigned int node
  )
{
  return pl[node].listEntry.next;
}

int
listIsTheLast(
  PASS_TYPE *pl,
  unsigned int node
  )
{

  return(pl[node].listEntry.next == END_LIST);
}

unsigned int
listPop(
  PASS_TYPE *pl,
  LIST_HT *listHt
  )
{

  unsigned int popEntry;

  popEntry = listHt->head;
  listHt->head = pl[listHt->head].listEntry.next;

  return popEntry;
}

int
listUpdateTail(
  PASS_TYPE *pl,
  LIST_HT *listHt
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
  PASS_TYPE *pl,
  LIST_HT *listHt
  )
{

  unsigned int node;
  PASS_TYPE *passEntry = NULL;

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


