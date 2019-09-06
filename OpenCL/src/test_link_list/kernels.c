
#ifndef __kernel
#define __kernel
#endif

#ifndef __global
#define __global
#endif


typedef struct {
  unsigned int    pass_id;
  unsigned short  orig_stop;
  unsigned short  dest_stop;
  unsigned short  arrival_time;
  unsigned short  alight_time;
  unsigned char  status;
} __attribute__ ((packed)) PassType;

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


__kernel void test1(
    __global const PASS_TYPE *stops_in
    )
{
  int gid = get_global_id(0);
  printf("hello host from kernel #%d\n", gid);


}

