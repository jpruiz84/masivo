#define STOP_MAX_PASS     10000
#define PRINT_LIST        0

#define BUS_MAX_PASS      250
#define MAX_STOPS         500

#define PASS_STATUS_EMPTY_255   255
#define PASS_STATUS_EMPTY         0
#define PASS_STATUS_TO_ARRIVE     1
#define PASS_STATUS_ARRIVED       2
#define PASS_STATUS_IN_BUS        3
#define PASS_STATUS_ALIGHTED      4

#define FALSE  0
#define TRUE   1

typedef struct {
  unsigned int    pass_id;
  unsigned short  orig_stop;
  unsigned short  dest_stop;
  unsigned short  arrival_time;
  unsigned short  alight_time;
  unsigned char   status;
} __attribute__ ((packed)) PassType;

// Stop Passengers Struct List (SPSL)
typedef struct {
  unsigned short  stop_num;
  unsigned int    total;
  unsigned int    last_empty;
  unsigned int    w_index;
  PassType        spl[STOP_MAX_PASS];
} __attribute__ ((packed)) SpslType;

// Bus Passengers Struct List (BPSL)
typedef struct {
  unsigned short  curr_stop;
  unsigned short  last_stop_i;
  unsigned short  total_stops;
  unsigned short  stops_num[MAX_STOPS];
  unsigned int    total;
  unsigned int    last_empty;
  unsigned int    w_index;
  PassType        bpl[BUS_MAX_PASS];
} __attribute__ ((packed)) BpslType;

__kernel void move_pass(
    __global SpslType *pass_list,
    __global SpslType *pass_arrival_list,
    unsigned int stops_size,
    unsigned int max_sim_time
    )
{
  int i = get_global_id(0);
  //printf("hello host from kernel #%d\n", gid);

  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (i >= stops_size){
    return;
  }

#if PRINT_LIST
    printf("\nPre pass_arrival_list %d, total %d, wIndex %d\n" ,
           pass_arrival_list[i].stop_num, pass_arrival_list[i].total, pass_arrival_list[i].w_index);
    for (int j = 0; j < pass_arrival_list[i].total; ++j) {
      printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, status %d\n",
             pass_arrival_list[i].spl[j].pass_id,
             pass_arrival_list[i].spl[j].orig_stop,
             pass_arrival_list[i].spl[j].dest_stop,
             pass_arrival_list[i].spl[j].arrival_time,
             pass_arrival_list[i].spl[j].alight_time,
             pass_arrival_list[i].spl[j].status);
    }
#endif

    unsigned int w;

    for (int sim_time = 0; sim_time < max_sim_time; ++sim_time) {
      //printf("In i %d total: %d\n", i, pass_arrival_list[i].total);
      if(pass_arrival_list[i].total > 0){
        #if 1
        //printf("sim_time: %d\n", sim_time);
        while(1){
          //printf("pass_id(%d): %d\n", pass_arrival_list[i].w_index, pass_arrival_list[i].spl[pass_arrival_list[i].w_index].pass_id);

          w = pass_arrival_list[i].w_index;
          if(w >= STOP_MAX_PASS){
            break;
          }

          if(pass_arrival_list[i].spl[w].status != 1){
            break;
          }

          if(sim_time < pass_arrival_list[i].spl[w].arrival_time){
            break;
          }

          //printf("In i %d moving pass_id(%d): %d\n", i, w, pass_arrival_list[i].spl[w].pass_id);

          pass_list[i].spl[pass_list[i].last_empty] = pass_arrival_list[i].spl[w];
          pass_list[i].spl[pass_list[i].last_empty].status = 2;
          pass_list[i].last_empty ++;
          pass_list[i].total ++;

          pass_arrival_list[i].spl[w].status = 0;
          pass_arrival_list[i].w_index ++;
          pass_arrival_list[i].total --;
          pass_arrival_list[i].last_empty --;

          if(pass_arrival_list[i].total == 0){
            break;
          }

          //printf("2 pass_id(%d): %d\n", pass_arrival_list[i].w_index, pass_arrival_list[i].spl[pass_arrival_list[i].w_index].arrival_time);

        }
        #endif
      }
    }

  #if PRINT_LIST
    printf("\nPost pass_arrival_list %d, total %d, wIndex %d\n" ,
           pass_arrival_list[i].stop_num, pass_arrival_list[i].total, pass_arrival_list[i].w_index);
    for (int j = 0; j < pass_arrival_list[i].total; ++j) {
      printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, status %d\n",
             pass_arrival_list[i].spl[j].pass_id,
             pass_arrival_list[i].spl[j].orig_stop,
             pass_arrival_list[i].spl[j].dest_stop,
             pass_arrival_list[i].spl[j].arrival_time,
             pass_arrival_list[i].spl[j].alight_time,
             pass_arrival_list[i].spl[j].status);
    }

        printf("\nPost pass list %d, total %d, wIndex %d\n" ,
           pass_list[i].stop_num, pass_list[i].total, pass_list[i].w_index);
    for (int j = 0; j < pass_list[i].total; ++j) {
      printf("passId %d, origStop %d, destStop %d, arrivalTime %d, alightTime %d, status %d\n",
             pass_list[i].spl[j].pass_id,
             pass_list[i].spl[j].orig_stop,
             pass_list[i].spl[j].dest_stop,
             pass_list[i].spl[j].arrival_time,
             pass_list[i].spl[j].alight_time,
             pass_list[i].spl[j].status);
    }
  #endif
}
