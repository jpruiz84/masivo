typedef struct {
  unsigned int    pass_id;
  unsigned short  orig_stop;
  unsigned short  dest_stop;
  unsigned short  arrival_time;
  unsigned short  alight_time;
  unsigned char   status;
} __attribute__ ((packed)) PassType;


typedef struct {
  unsigned int    total;
  unsigned int    last_empty;
  unsigned int    w_index;
  PassType        spl[1000];
} __attribute__ ((packed)) SpslType;


__kernel void move_pass(
    __global SpslType *pass_list,
    __global SpslType *pass_arrival_list,
    unsigned int stops_size,
    unsigned int pass_size,
    unsigned int sim_time
    )
{
  int gid = get_global_id(0);
  //printf("hello host from kernel #%d\n", gid);

  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (gid >= stops_size)
  {
      return;
  }

#if 0
  printf("pass_arrival_list.total(%d): %d\n", gid, pass_arrival_list->total);
  printf("pass_arrival_list.last_empty(%d): %d\n", gid, pass_arrival_list->last_empty);
  //printf("SPL(%d): %d\n", 0, (0 + &pass_arrival_list[0*(pass_size + 8)].spl)->arrival_time);
  //printf("SPL(%d): %d\n", 1, (0 + &pass_arrival_list[1*(pass_size + 8)].spl)->arrival_time);

  for (int i = 0; i < 10; i++){
    printf("SPL(%d)(%d): %d\n", gid, i,  pass_arrival_list[gid].spl[i].arrival_time);
  }

  for (int i = 0; i < 3; i++){
    *(pass_list + i) = *(pass_arrival_list + i);
  }

#endif

  unsigned int w;

  //printf("In gid %d total: %d\n", gid, pass_arrival_list[gid].total);
  if(pass_arrival_list[gid].total > 0){
    #if 1
    //printf("sim_time: %d\n", sim_time);
    while(1){
      //printf("pass_id(%d): %d\n", pass_arrival_list[gid].w_index, pass_arrival_list[gid].spl[pass_arrival_list[gid].w_index].pass_id);

      w = pass_arrival_list[gid].w_index;
      if(w >= pass_size){
        break;
      }

      if(pass_arrival_list[gid].spl[w].status != 1){
        break;
      }

      if(sim_time < pass_arrival_list[gid].spl[w].arrival_time){
        break;
      }

      //printf("In gid %d moving pass_id(%d): %d\n", gid, w, pass_arrival_list[gid].spl[w].pass_id);

      pass_list[gid].spl[pass_list[gid].last_empty] = pass_arrival_list[gid].spl[w];
      pass_list[gid].spl[pass_list[gid].last_empty].status = 2;
      pass_list[gid].last_empty ++;
      pass_list[gid].total ++;

      pass_arrival_list[gid].spl[w].status = 0;
      pass_arrival_list[gid].w_index ++;
      pass_arrival_list[gid].total --;
      pass_arrival_list[gid].last_empty --;

      if(pass_arrival_list[gid].total == 0){
        break;
      }

      //printf("2 pass_id(%d): %d\n", pass_arrival_list[gid].w_index, pass_arrival_list[gid].spl[pass_arrival_list[gid].w_index].arrival_time);


    }
    #endif
  }
}
