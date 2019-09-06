#ifndef __OPENCL_VERSION__
#define __kernel
#define __global
#endif
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
}__attribute__ ((packed)) PASS_TYPE;

typedef struct {
  unsigned int total;
  LIST_HT listHt;
}__attribute__ ((packed))
SLS_TYPE;


__kernel void movePass(
    __global PASS_TYPE *passList,
    __global SLS_TYPE *stopsArrival,
    __global SLS_TYPE *stopsQueue,
    unsigned int simTime
    )
{
  int gid = get_global_id(0);

  int i = 0;
  printf("simTime: %d\n", simTime);
  printf("(%d) paddId %d, arrivalTime %d\n", i, passList[i].passId, passList[i].arrivalTime);
  passList[i].passId = 8484;
  printf("(%d) paddId %d, arrivalTime %d\n", i, passList[i].passId, passList[i].arrivalTime);

}


__kernel void test1(
    __global PASS_TYPE *passList
    )
{
  int gid = get_global_id(0);

  int i = 0;

  printf("(%d) paddId %d, arrivalTime %d\n", i, passList[i].passId, passList[i].arrivalTime);
  passList[i].passId = 8484;
  printf("(%d) paddId %d, arrivalTime %d\n", i, passList[i].passId, passList[i].arrivalTime);

}

