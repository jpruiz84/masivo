
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

