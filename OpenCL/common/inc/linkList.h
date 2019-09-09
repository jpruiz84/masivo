#ifndef LINKLIST_H_
#define LINKLIST_H_


#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */

#define EMPTY_LIST   (unsigned int)4294967295
#define END_LIST     (unsigned int)4294967295


#define BASE_CR(Record, TYPE, Field)  ((TYPE *) ((char *) (Record) - (char *) &(((TYPE *) 0)->Field)))

typedef struct _LIST_ENTRY LIST_ENTRY;
struct _LIST_ENTRY
{
  unsigned int next;
} __attribute__ ((packed));

typedef struct {
  unsigned int head;
  unsigned int tail;
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


typedef struct {
  unsigned int total;
  LIST_HT listHt;
}__attribute__ ((packed))
SLS_TYPE;

#define PASS_FROM_THIS(a) BASE_CR (a, PASS_TYPE, listEntry)


int
listInit(
  LIST_HT *listHt
  );

int
listInsert(
  PASS_TYPE *pl,
  LIST_HT *listHt,
  unsigned int entry
  );

int
listIsEmpty(
  LIST_HT *listHt
  );


unsigned int
listGetFirstNode(
  LIST_HT *listHt
  );


unsigned int
listGetNextNode(
  PASS_TYPE *pl,
  unsigned int node
  );

int
listIsTheLast(
  PASS_TYPE *pl,
  unsigned int node
  );

unsigned int
listPop(
  PASS_TYPE *pl,
  LIST_HT *listHt
  );

int
listUpdateTail(
  PASS_TYPE *pl,
  LIST_HT *listHt
  );

int
listPrintPass(
  PASS_TYPE *pl,
  LIST_HT *listHt
  );


#endif // LINKLIST_H_
