
#ifndef MERGESORT_H_
#define MERGESORT_H_

#include <string.h>
#include "linkList.h"

#define Node unsigned int

void
MergeSort(
  PASS_TYPE *pl,
  Node *headRef);

void
sortByArrivalTime(
  PASS_TYPE *pl,
  LIST_HT* listHt
  );

#endif /*MERGESORT_H_ */
