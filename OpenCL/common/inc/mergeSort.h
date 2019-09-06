
#ifndef MERGESORT_H_
#define MERGESORT_H_

#include <string.h>
#include "linkList.h"

#define Node LIST_ENTRY

int
swap(
  LIST_ENTRY *nodeA,
  LIST_ENTRY *nodeB
  );


int
listBubleSortByArrivalTime(
  LIST_HT *listHt
  );



int
getLength(
  LIST_ENTRY *listHt
  );

void MergeSort(Node** headRef);

void
sortByArrivalTime(
  LIST_HT* listHt
  );

#endif /*MERGESORT_H_ */
