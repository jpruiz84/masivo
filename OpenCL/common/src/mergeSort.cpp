#include <stdio.h>      /* printf, scanf, puts, NULL */
#include "mergeSort.h"

/* function prototypes */
Node* SortedMerge(Node* a, Node* b);
void FrontBackSplit(Node* source,
                    Node** frontRef, Node** backRef);

void
sortByArrivalTime(
  LIST_HT* listHt
  )
{
  MergeSort(&listHt->head);
  listUpdateTail(listHt);
}


/* sorts the linked list by changing next pointers (not data) */
void
MergeSort(Node **headRef)
{
  Node *head = *headRef;
  Node *a;
  Node *b;

  /* Base case -- length 0 or 1 */
  if((head == NULL) || (head->next == NULL)){
    return;
  }

  /* Split head into 'a' and 'b' sublists */
  FrontBackSplit(head, &a, &b);

  /* Recursively sort the sublists */
  MergeSort(&a);
  MergeSort(&b);

  /* answer = merge the two sorted lists together */
  *headRef = SortedMerge(a, b);
}

/* See https:// www.geeksforgeeks.org/?p=3622 for details of this
 function */
Node*
SortedMerge(Node *a, Node *b)
{
  Node *result = NULL;

  /* Base cases */
  if(a == NULL)
    return (b);
  else if(b == NULL)
    return (a);

  /* Pick either a or b, and recur */
  //if (a->data <= b->data) {
  if(PASS_FROM_THIS(a)->arrivalTime <= PASS_FROM_THIS(b)->arrivalTime){
    result = a;
    result->next = SortedMerge(a->next, b);
  }
  else{
    result = b;
    result->next = SortedMerge(a, b->next);
  }
  return (result);
}

/* UTILITY FUNCTIONS */
/* Split the nodes of the given list into front and back halves,
 and return the two lists using the reference parameters.
 If the length is odd, the extra node should go in the front list.
 Uses the fast/slow pointer strategy. */
void
FrontBackSplit(Node *source,
Node **frontRef, Node **backRef)
{
  Node *fast;
  Node *slow;
  slow = source;
  fast = source->next;

  /* Advance 'fast' two nodes, and advance 'slow' one node */
  while(fast != NULL){
    fast = fast->next;
    if(fast != NULL){
      slow = slow->next;
      fast = fast->next;
    }
  }

  /* 'slow' is before the midpoint in the list, so split it in two
   at that point. */
  *frontRef = source;
  *backRef = slow->next;
  slow->next = NULL;
}
