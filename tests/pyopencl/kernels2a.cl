typedef struct {
  unsigned int    pass_id;
  unsigned short  orig_stop;
  unsigned short  dest_stop;
  unsigned short  arrival_time;
  unsigned short  alight_time;
  unsigned char  status;
} __attribute__ ((packed)) PassType;


__kernel void move_pass2a(
    __global PassType *total_pass_list,
    __global unsigned int *last_index,
    unsigned int stops_size,  
    unsigned int pass_size,
    unsigned int sim_time
    )
{
  int gid = get_global_id(0);
  unsigned int j = 0;
  
  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (gid >= stops_size)
  {   
      return; 
  }

  #if 0
  //printf("size of: %d\n", sizeof(PassType));
  for (int i = 0; i < pass_size; i++){

    if(total_pass_list[gid*pass_size + i].arrival_time > sim_time){
      total_pass_list[gid*pass_size + i].status = 2;
    }
  }
  #else
  j = last_index[gid];
  while(1){
    if(total_pass_list[gid*pass_size + j].arrival_time == sim_time){
      total_pass_list[gid*pass_size + j].status = 2;
      j ++;
    }
    else{
      last_index[gid] = j;
      break;
    }
  }
  
  
  #endif

  /*
  for i in range(len(total_pass_list_py)):
  j = int(last_index[i])
  while True:
    if total_pass_list_py[i][j]['arrival_time'] == SIM_TIME:
      total_pass_list_py[i][j]['status'] = globalConstants.PASS_STATUS_ARRIVED
      j += 1
    else:
      last_index[i] = j
      break
  
  */ 

}
