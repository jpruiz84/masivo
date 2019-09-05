#ifndef LINKLIST_H_
#define LINKLIST_H_


#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */



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
  LIST_HT *listHt,
  LIST_ENTRY *entry
  );

int
listIsEmpty(
  LIST_HT *listHt
  );


LIST_ENTRY*
listGetFirstNode(
  LIST_HT *listHt
  );


LIST_ENTRY*
listGetNextNode(
  LIST_ENTRY *Node
  );

int
listIsTheLast(
  LIST_ENTRY *Node
  );

LIST_ENTRY*
listPop(
  LIST_HT *listHt
  );


#endif // LINKLIST_H_
