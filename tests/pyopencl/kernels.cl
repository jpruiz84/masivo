
__kernel void sum(
    __global unsigned int *res_g,
    unsigned int count_to,  
    unsigned int iNumElements
    )
{
  int gid = get_global_id(0);
  
  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (gid >= iNumElements)
  {   
      return; 
  }
  
  for (int i = 0; i < count_to; i++){
    res_g[gid] += 1;
  }
}

__kernel void move(
    __global const unsigned int *stops_in,
    __global unsigned int *stops_out,
    unsigned int stops_size,  
    unsigned int pass_size
    )
{
  int gid = get_global_id(0);
  //printf("hello host from kernel #%d\n", gid);
  
  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (gid >= stops_size)
  {   
      return; 
  }

  for (int i = 0; i < pass_size; i++){
    //printf("stops_in %d\n", *(stops_in + gid*pass_size + i));
    if(((*(stops_in + gid*pass_size + i)) % 1000000) > 10){
      *(stops_out + gid*pass_size + i) = *(stops_in + gid*pass_size + i);
    }
    //printf("stops_out %d\n", *(stops_out + gid*pass_size + i));
    //*(stops_out + i) = *(stops_in + i);
  }
}

//PASS_TYPE = np.dtype([('pass_id', 'u4'), ('orig_stop', 'u2'), ('dest_stop', 'u2'),
//                      ('arrival_time', 'u2'), ('alight_time', 'u2'), ('status', 'u1')])

typedef struct {
  unsigned int    pass_id;
  unsigned short  orig_stop;
  unsigned short  dest_stop;
  unsigned short  arrival_time;
  unsigned short  alight_time;
  unsigned char  status;
} __attribute__ ((packed)) PassType;


__kernel void move_pass(
    __global const PassType *stops_in,
    __global PassType *stops_out,
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
      stops_list[gid*pass_size + i].status = 1;
    }
  }
}
