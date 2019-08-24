#define STOP_MAX_PASS   10000
#define BUS_MAX_PASS      100
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


__kernel void masivo_runner(
    __global SpslType *pass_list,
    __global SpslType *pass_arrival_list,
    __global SpslType *pass_alight_list,
    __global BpslType *buses_pass_list,
    unsigned int total_stops,                     // Total stops
    unsigned int total_buses,                     // Total stops
    unsigned int sim_time
    )
{
  int gid = get_global_id(0);
  unsigned int w;
  char bus_for_dest;
  unsigned int j,k,l,n;

  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (gid >= total_stops){   
      return; 
  }


  // STOPS ARRIVAL:
  //printf("In gid %d total: %d\n", gid, pass_arrival_list[gid].total);
  if(pass_arrival_list[gid].total > 0){
    #if 1
    //printf("sim_time: %d\n", sim_time);
    while(1){
      //printf("pass_id(%d): %d\n", pass_arrival_list[gid].w_index, pass_arrival_list[gid].spl[pass_arrival_list[gid].w_index].pass_id);
      
      
      w = pass_arrival_list[gid].w_index;
      // Check if the list is finished
      if(w >= STOP_MAX_PASS){
        break;
      }

      // Check pass status
      if(pass_arrival_list[gid].spl[w].status != PASS_STATUS_TO_ARRIVE){
        break;
      }

      // Check arrival time
      if(sim_time < pass_arrival_list[gid].spl[w].arrival_time){
        break;
      }

      //printf("In gid %d moving pass_id(%d): %d\n", gid, w, pass_arrival_list[gid].spl[w].pass_id);

      pass_list[gid].spl[pass_list[gid].last_empty] = pass_arrival_list[gid].spl[w];
      pass_list[gid].spl[pass_list[gid].last_empty].status = PASS_STATUS_ARRIVED;
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
#if 1

  // For each bus
  for(j = 0; j < total_buses; j++){
    // If the bus is in the stop
    if(pass_list[gid].stop_num == buses_pass_list[j].curr_stop){

      // ALIGHTING
      // Only if there are passengers in the bus
      if(buses_pass_list[j].total > 0){
        // For each pass in the bus
        for(k = 0; k < BUS_MAX_PASS; k++){
          //printf("pass id to check(%d): %d\n" k, buses_pass_list[j].bpl[k].pass_id)
          // If the pass is in the bus
          if(buses_pass_list[j].bpl[k].status == PASS_STATUS_IN_BUS){
            // If the stop is the pass dest stop
            if(buses_pass_list[j].bpl[k].dest_stop == pass_list[gid].stop_num){
              //printf("ALIGHTING pass id %d from bus %d to stop %d\n", buses_pass_list[j].bpl[k].pass_id, j, pass_list[gid].stop_num);

              buses_pass_list[j].bpl[k].status = PASS_STATUS_ALIGHTED;
              buses_pass_list[j].total -= 1;
              buses_pass_list[j].last_empty -= 1;

              n = pass_alight_list[gid].last_empty;
              pass_alight_list[gid].spl[n] = buses_pass_list[j].bpl[k];
              pass_alight_list[gid].total += 1;
              pass_alight_list[gid].last_empty += 1;
            }
          }
        }// End For each pass in the bus, for(k = 0; k < BUS_MAX_PASS; k++)

      } // End Only if there are passengers in the bus, if(buses_pass_list[j].total > 0)

      // BOARDING
      // If there are pass in the stop, do not look for more buses
      if(pass_list[gid].total == 0){
        break;
      }

      // If the bus is full, continue with the next bus
      if(buses_pass_list[j].total >= BUS_MAX_PASS){
        continue;
      }

      // For this bus, begin the free space search from the beginning
      buses_pass_list[j].last_empty = 0;
      //printf("Bus %d in the stop %d\n", j, pass_list[gid].stop_num);

      // For each pass in the stop
      for(k = 0; k < STOP_MAX_PASS; k++){
        //printf("Check for board pass_id %d\n", (pass_list[gid].spl[k]));
        
        // If the bus is full, continue with the next bus
        if(buses_pass_list[j].total >= BUS_MAX_PASS){
          break;
        }

        // If we are at the end of the pass list
        if(pass_list[gid].spl[k].status == PASS_STATUS_EMPTY_255){
          break;
        }

        // If the pass has arrived to the stop
        if(pass_list[gid].spl[k].status == PASS_STATUS_ARRIVED){
          
          // Check if the bus route has the pass destination stop
          bus_for_dest = FALSE;
          for(l = buses_pass_list[j].last_stop_i + 1; l < buses_pass_list[j].total_stops; l++){
            if(l < 5){
              //printf("Stops to(%d): %d, last_stop_i %d, curr_stop %d\n", l, buses_pass_list[j].stops_num[l], buses_pass_list[j].last_stop_i, buses_pass_list[j].curr_stop);
            }
            if(pass_list[gid].spl[k].dest_stop == buses_pass_list[j].stops_num[l]){
              bus_for_dest = TRUE;
              break;
            }
          }

          // If the bus has the destination stop, pass boards
          if(bus_for_dest){
            // Look for a free space in the bus
            for(n = buses_pass_list[j].last_empty; n < BUS_MAX_PASS; n++){
              //printf("bus seat: %d, status: %d\n",n, buses_pass_list[j].bpl[n].status);

              if(buses_pass_list[j].bpl[n].status == PASS_STATUS_IN_BUS){
                //printf("busy\n");
                continue;
              }

              //printf("BOARDING pass_id %d to the bus %d, in seat %d\n", pass_list[gid].spl[k].pass_id, j, n);

              pass_list[gid].spl[k].status = PASS_STATUS_IN_BUS;
              pass_list[gid].total -= 1;

              buses_pass_list[j].bpl[n] = pass_list[gid].spl[k];
              buses_pass_list[j].total += 1;
              buses_pass_list[j].last_empty = n;

              break;
            
            } // End // Look for a free space in the bus

            



          } // End If the bus has the destination stop, pass boards  if(bus_for_dest)

          // If bus is full break to go to the next bus in the stop
          if(buses_pass_list[j].total >= BUS_MAX_PASS){
            break;
          }


        } // End If the pass have arrived to the stop if(pass_list[gid].spl[k].status == PASS_STATUS_ARRIVED)

      
      
      
      } // End For each pass in the stop for(int k = 0; k < STOP_MAX_PASS; k++)


    } // End If the bus is in the stop
    

  }// End For each bus for(int j = 0; j < total_buses; j++)
  
#endif
}


__kernel void move_pass(
    __global SpslType *pass_list,
    __global SpslType *pass_arrival_list,
    unsigned int total_stops,  
    unsigned int sim_time
    )
{
  int gid = get_global_id(0);
  //printf("hello host from kernel #%d\n", gid);
  
  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (gid >= total_stops)
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
      if(w >= STOP_MAX_PASS){
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
