#include <stdio.h>      /* printf, scanf, puts, NULL */
#include "mergeSort.h"

/* function prototypes */
Node
SortedMerge(
  PASS_TYPE *pl,
  Node *a,
  Node *b);

void FrontBackSplit(
  PASS_TYPE *pl,
  Node source,
  Node *frontRef,
  Node *backRef);

void
sortByArrivalTime(
  PASS_TYPE *pl,
  LIST_HT* listHt
  )
{
  MergeSort(pl, &listHt->head);
  listUpdateTail(pl, listHt);
}


/* sorts the linked list by changing next pointers (not data) */
void
MergeSort(
  PASS_TYPE *pl,
  Node *headRef)
{
  Node head = *headRef;
  Node a;
  Node b;

  /* Base case -- length 0 or 1 */
  if((head == END_LIST) || (pl[head].listEntry.next == END_LIST)){
    return;
  }


  /* Split head into 'a' and 'b' sublists */
  FrontBackSplit(pl, head, &a, &b);

  /* Recursively sort the sublists */
  MergeSort(pl, &a);
  MergeSort(pl, &b);

  /* answer = merge the two sorted lists together */
  *headRef = SortedMerge(pl, &a, &b);
}

/* See https:// www.geeksforgeeks.org/?p=3622 for details of this
 function */
Node
SortedMerge(
  PASS_TYPE *pl,
  Node *a,
  Node *b
  )
{
  Node result = END_LIST;

  /* Base cases */
  if(*a == END_LIST)
    return (*b);
  else if(*b == END_LIST)
    return (*a);

  /* Pick either a or b, and recur */
  //if (a->data <= b->data) {
  if(pl[*a].arrivalTime <= pl[*b].arrivalTime){

    result = *a;
    pl[result].listEntry.next = SortedMerge(pl, &pl[*a].listEntry.next, b);
  }
  else{

    result = *b;
    pl[result].listEntry.next = SortedMerge(pl, a, &pl[*b].listEntry.next);
  }
  return (result);
}

/* UTILITY FUNCTIONS */
/* Split the nodes of the given list into front and back halves,
 and return the two lists using the reference parameters.
 If the length is odd, the extra node should go in the front list.
 Uses the fast/slow pointer strategy. */
void
FrontBackSplit(
  PASS_TYPE *pl,
  Node source,
  Node *frontRef,
  Node *backRef
  )
{
  Node fast;
  Node slow;
  slow = source;
  fast = pl[source].listEntry.next;

  /* Advance 'fast' two nodes, and advance 'slow' one node */
  while(fast != END_LIST){
    fast = pl[fast].listEntry.next;
    if(fast != END_LIST){
      slow = pl[slow].listEntry.next;
      fast = pl[fast].listEntry.next;
    }
  }

  /* 'slow' is before the midpoint in the list, so split it in two
   at that point. */
  *frontRef = source;
  *backRef = pl[slow].listEntry.next;
  pl[slow].listEntry.next = END_LIST;
}
