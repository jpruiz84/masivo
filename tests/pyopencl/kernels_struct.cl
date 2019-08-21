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
  PassType        spl[10000];
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
  

/*
    if len(self.pass_arrival_list) > 0:
      while sim_time == self.pass_arrival_list[0]['arrival_time']:
        self.pass_in(self.pass_arrival_list.pop(0))
        if len(self.pass_arrival_list) == 0:
          break
*/


  if(pass_arrival_list[gid].total > 0){
    #if 1
    //printf("sim_time: %d\n", sim_time);
    while(sim_time == pass_arrival_list[gid].spl[pass_arrival_list[gid].w_index].arrival_time){
      //printf("pass_id(%d): %d\n", pass_arrival_list[gid].w_index, pass_arrival_list[gid].spl[pass_arrival_list[gid].w_index].arrival_time);
      
      
      pass_list[gid].spl[pass_list[gid].last_empty] = pass_arrival_list[gid].spl[pass_arrival_list[gid].w_index];
      pass_list[gid].spl[pass_list[gid].last_empty].status = 2;
      pass_list[gid].last_empty ++;
      pass_list[gid].total ++;

      pass_arrival_list[gid].spl[pass_arrival_list[gid].w_index].status = 0;
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

  

    /*
  //printf("size of: %d\n", sizeof(PassType));
  for (int i = 0; i < pass_size; i++){

    //((PassType)(*(stops_out + gid*pass_size + i))).pass_id = 1;
    //for (int j = 0; j < sizeof(PassType); j++){
    //  stops_out[gid*pass_size + i + j] = stops_in[gid*pass_size + i + j];
    //}

    stops_out[gid*pass_size + i].pass_id = stops_in[gid*pass_size + i].pass_id;
    stops_out[gid*pass_size + i].orig_stop = stops_in[gid*pass_size + i].orig_stop;
    stops_out[gid*pass_size + i].dest_stop = stops_in[gid*pass_size + i].dest_stop;
    stops_out[gid*pass_size + i].arrival_time = stops_in[gid*pass_size + i].arrival_time;
    stops_out[gid*pass_size + i].alight_time = stops_in[gid*pass_size + i].alight_time;
    stops_out[gid*pass_size + i].status = stops_in[gid*pass_size + i].status;


    if(stops_out[gid*pass_size + i].arrival_time > sim_time){
      stops_out[gid*pass_size + i].status = 1;
    }

  }
*/  

}

__kernel void move_pass2(
    __global PassType *stops_list,
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

  //printf("size of: %d\n", sizeof(PassType));
  for (int i = 0; i < pass_size; i++){

    if(stops_list[gid*pass_size + i].arrival_time > sim_time){
      stops_list[gid*pass_size + i].status = 2;
    }
  }
}

__kernel void move_pass3(
    __global PassType *pass_list,
    unsigned int pass_size,
    unsigned int sim_time
    )
{
  int gid = get_global_id(0);
  //printf("hello host from kernel #%d\n", gid);
  
  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (gid >= pass_size)
  {   
      return; 
  }
  if(pass_list[gid].arrival_time > sim_time){
    pass_list[gid].status = 2;
  }
}
