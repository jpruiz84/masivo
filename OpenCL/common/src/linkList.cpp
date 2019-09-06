#include "linkList.h"


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
  return (listHt->tail == NULL || listHt->head == NULL);
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

LIST_ENTRY*
listPop(
  LIST_HT *listHt
  )
{

  LIST_ENTRY* popEntry;

  popEntry = listHt->head;
  listHt->head = listHt->head->next;

  return popEntry;
}

int
listUpdateTail(
  LIST_HT *listHt
  )
{
  LIST_ENTRY* cur = listHt->head;

  while(!cur->next){
    cur = cur->next;
  }

  listHt->tail = cur;


  return 0;
}

int
listPrintPass(
  LIST_HT *listHt
  )
{

  LIST_ENTRY *node;
  PASS_TYPE *passEntry = NULL;

  if(listIsEmpty (listHt)){
    return -1;
  }

  node = listGetFirstNode(listHt);
  do {
    passEntry = PASS_FROM_THIS(node);
    printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, cur: %p, next: %p\n",
      passEntry->passId, passEntry->origStop, passEntry->destStop,
      passEntry->arrivalTime, passEntry->alightTime, &passEntry->listEntry, passEntry->listEntry.next);

    node = listGetNextNode(node);

  }while(node);

  return 0;
}


