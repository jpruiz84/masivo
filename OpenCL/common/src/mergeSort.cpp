#include "mergeSort.h"

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
listBubleSortByArrivalTime(
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

