#ifndef __OPENCL_VERSION__
#define __kernel
#define __global
#define __local
#endif

#define STOP_MAX_PASS   10000
#define BUS_MAX_PASS      250
#define MAX_STOPS         500

#define PASS_STATUS_END_LIST    255
#define PASS_STATUS_EMPTY         0
#define PASS_STATUS_TO_ARRIVE     1
#define PASS_STATUS_ARRIVED       2
#define PASS_STATUS_IN_BUS        3
#define PASS_STATUS_ALIGHTED      4

#define BUS_TRAVEL_SPEED_M_S         54*1000/3600
#define BUS_STOPPING_TIME            20

#define BUS_NOT_STARTED_STOP  20000
#define EMPTY_STOP_NUMBER     20000
#define BUS_TRAVELING         20001
#define BUS_FINISHED          20002

#define STOP_BUS_WINDOW_DISTANCE     10


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
  int             stop_pos;
  unsigned int    total;
  unsigned int    last_empty;
  unsigned int    w_index;
  PassType        spl[STOP_MAX_PASS];
} __attribute__ ((packed)) SpslType;

// Bus Passengers Struct List (BPSL)
typedef struct {
  unsigned short  number;
  short           travel_speed_m_s;
  int             start_pos;
  unsigned short  last_stop_table_i;
  int             last_stop_pos;
  unsigned int    start_time;
  unsigned short  stops_num_i;
  short           stop_inc;
  unsigned short  in_the_stop_counter;
  unsigned short  in_the_stop;
  int             curr_pos;
  unsigned short  curr_stop;
  unsigned short  last_stop_i;
  unsigned short  total_stops;
  unsigned short  stops_num[MAX_STOPS];
  unsigned int    total;
  PassType        bpl[BUS_MAX_PASS];
} __attribute__ ((packed)) BpslType;


__kernel void masivo_runner(
  __global SpslType *pwq,		// Passengers Waiting Queue
  __global SpslType *paq,		// Passengers Arrival Queue
  __global SpslType *plq,		// Passengers aLight Queue
  __global BpslType *bpa,		// Bus Passengers Array
  unsigned int total_stops,                     // Total stops
  unsigned int total_buses,                     // Total stops
  unsigned int sim_time
    )
{
  int gid = get_global_id(0);
  unsigned int w;
  char bus_for_dest;
  unsigned int i,j,k,l,n;
  char in_the_route;
  short next_stop_i;
  unsigned int last_empty_seat_in_bus;

  // bound check (equivalent to the limit on a 'for' loop for standard/serial C code
  if (gid >= total_stops){   
      return; 
  }

  // **************** PASSENGERS ARRIVING ********************************
  //printf("In gid %d total: %d\n", gid, pass_arrival_list[gid].total);
#if 1
  //printf("gid: %d, sim_time: %d\n", gid, sim_time);
  while(TRUE){
    //printf("pass_id(%d): %d\n", pass_arrival_list[gid].w_index, 
    //pass_arrival_list[gid].spl[pass_arrival_list[gid].w_index].pass_id);

    // Check if the arrival queue is empty 
    if(paq[gid].total == 0){
      break;
    }

    w = paq[gid].w_index;

    // Check arrival time
    if(paq[gid].spl[w].arrival_time > sim_time){
      break;
    }

    //printf("In gid %d moving pass_id(%d): %d\n", gid, w, pass_arrival_list[gid].spl[w].pass_id);
    pwq[gid].spl[pwq[gid].last_empty] = paq[gid].spl[w];
    pwq[gid].spl[pwq[gid].last_empty].status = PASS_STATUS_ARRIVED;
    pwq[gid].last_empty ++;
    pwq[gid].total ++;

    paq[gid].spl[w].status = 0;
    paq[gid].w_index ++;
    paq[gid].total --;

    //printf("2 pass_id(%d): %d\n", pass_arrival_list[gid].w_index,
    //pass_arrival_list[gid].spl[pass_arrival_list[gid].w_index].arrival_time);
  }
#endif
   
#if 1
  // For each bus
  for(j = 0; j < total_buses; j++){
    
    // If the bus is in the stop
    if(pwq[gid].stop_num == bpa[j].curr_stop){
    
      // **************** PASSENGERS ALIGHTING ********************************
    
      // Only if there are passengers in the bus
      if(bpa[j].total > 0){
        
        // For each passenger in the bus
        for(k = 0; k < BUS_MAX_PASS; k++){
          //printf("pass id to check(%d): %d\n" k, buses_pass_list[j].bpa[k].pass_id)
          
          // If the passenger status indicate that is the bus
          if(bpa[j].bpl[k].status == PASS_STATUS_IN_BUS){
            
            // If the stop is the passsenger destination stop
            if(bpa[j].bpl[k].dest_stop == pwq[gid].stop_num){
              //printf("ALIGHTING pass id %d from bus %d to stop %d\n", 
              //buses_struc_list[j].bpa[k].pass_id, j, stops_alight_list[gid].stop_num);

              // Move the passenger from the bus to the stop alight queue
              n = plq[gid].total;
              plq[gid].spl[n] = bpa[j].bpl[k];
              plq[gid].spl[n].status = PASS_STATUS_ALIGHTED;
              plq[gid].spl[n].alight_time = sim_time;
              plq[gid].total += 1;

              bpa[j].bpl[k].status = PASS_STATUS_EMPTY;
              bpa[j].total -= 1;
            }
          } // End if passger in the bus, if(buses_struc_list[j].bpa[k].status == PASS_STATUS_IN_BUS)
        }// End For each pass in the bus, for(k = 0; k < BUS_MAX_PASS; k++)

      } // End Only if there are passengers in the bus, if(buses_pass_list[j].total > 0)

      // **************** PASSENGERS BOARDING ********************************
      // If there are not passengers in the stop, do not look for more buses to boarding
      if(pwq[gid].total == 0){
        break;
      }

      // If the bus is full, continue with the next bus
      if(bpa[j].total >= BUS_MAX_PASS){
        continue;
      }

      // For this bus, begin the free space search from the beginning
      last_empty_seat_in_bus = 0;
      // For each passenger in the stop
      for(k = 0; k < STOP_MAX_PASS; k++){
        //printf("Check for board pass_id %d\n", (stops_queue_list[gid].spl[k].pass_id));

        // If the bus is full, continue with the next bus
        if(bpa[j].total >= BUS_MAX_PASS){
          break;
        }

        // If we are at the end of the passenger waiting queue, finish
        if(pwq[gid].spl[k].status == PASS_STATUS_END_LIST){
          break;
        }

        // If the passenger has arrived to the stop
        if(pwq[gid].spl[k].status == PASS_STATUS_ARRIVED){

          // Check if the bus route has the passenger destination stop
          bus_for_dest = FALSE;
          // For each remaining stops in bus's stop table
          for(l = bpa[j].last_stop_table_i; l < bpa[j].total_stops; l++){
            if(pwq[gid].spl[k].dest_stop == bpa[j].stops_num[l]){
              bus_for_dest = TRUE;
              break;
            }
          }

          // If the bus has the destination stop, passenger tryies to board this bus
          if(bus_for_dest){
            // Look for a free space in the bus
            for(n = last_empty_seat_in_bus; n < BUS_MAX_PASS; n++){
              //printf("bus seat: %d, status: %d\n",n, buses_struc_list[j].bpa[n].status);

              // If the seat in the bus is empty
              if(bpa[j].bpl[n].status == PASS_STATUS_EMPTY){

                //printf("BOARDING pass_id %d to the bus %d, in seat %d\n",
                //stops_queue_list[gid].spl[k].pass_id, j, n);

                // Move passenger from stop wating queue to the bus
                bpa[j].bpl[n] = pwq[gid].spl[k];
                bpa[j].bpl[n].status = PASS_STATUS_IN_BUS;
                bpa[j].total += 1;

                pwq[gid].spl[k].status = PASS_STATUS_EMPTY;
                pwq[gid].total -= 1;

                last_empty_seat_in_bus = n;
                break;

              }

            } // End // Look for a free space in the bus

          } // End If the bus has the destination stop, pass boards  if(bus_for_dest)

          // If bus is full break to go to the next bus in the stop
          if(bpa[j].total >= BUS_MAX_PASS){
            break;
          }

        } // End If the pass have arrived to the stop if(pass_list[gid].spl[k].status == PASS_STATUS_ARRIVED)

      } // End For each pass in the stop for(int k = 0; k < STOP_MAX_PASS; k++)

    } // End If the bus is in the stop

  }// End For each bus for(int j = 0; j < total_buses; j++)

#endif


  // **************** UPDATE BUSES POSITION ********************************
#if 1
  if(gid == 0){
    // Update buses
    // For each bus
    for(int i = 0; i < total_buses; ++i){
      // Do not process finished buses
      if(bpa[i].curr_stop == BUS_FINISHED){
        continue;
      }

      // Check if start the bus
      if(bpa[i].curr_stop == BUS_NOT_STARTED_STOP){
        if(sim_time >= bpa[i].start_time){
          bpa[i].in_the_stop = TRUE;
          bpa[i].curr_stop = bpa[i].stops_num[0];
          bpa[i].last_stop_i = bpa[i].stops_num[0];
          bpa[i].curr_pos = bpa[i].start_pos;
          bpa[i].last_stop_pos = bpa[i].curr_pos;

          //printf("Starting bus %d in stop %d start time %d\n",
          //             buses_struc_list[i].number,
          //             buses_struc_list[i].curr_stop,
          //             buses_struc_list[i].start_time);
        }
        continue;
      }


      // Update bus position

      // if waiting in the stop
      //printf("Bus: %d, in_the_stop_flag: %d, curr_stop %d, pos: %d\n",
      //       buses_struc_list[i].number,
      //       buses_struc_list[i].in_the_stop,
      //       buses_struc_list[i].curr_stop,
      //       buses_struc_list[i].curr_pos);

      // Check if we have to depart from the stop
      if(bpa[i].in_the_stop){
        bpa[i].in_the_stop_counter -= 1;
        if(bpa[i].in_the_stop_counter == 0){
          bpa[i].last_stop_table_i += 1;
          bpa[i].in_the_stop = FALSE;
          bpa[i].curr_stop = BUS_TRAVELING;
        }
      }

      // if I am not waiting in a stop, go ahead
      if(bpa[i].curr_stop == BUS_TRAVELING){

        if(bpa[i].curr_pos > 1000 && bpa[i].curr_pos < 3000){
          bpa[i].curr_pos += bpa[i].travel_speed_m_s;
        }else{
          bpa[i].curr_pos += bpa[i].travel_speed_m_s;
        }


      }

      // Check if the bus has to leave the current stop, if not, do not check for other stop
      if(abs(bpa[i].last_stop_pos - bpa[i].curr_pos)
          < STOP_BUS_WINDOW_DISTANCE){
        continue;
      }


      // Check if the bus is at the next stop
      next_stop_i = (short)bpa[i].last_stop_i + bpa[i].stop_inc;

      // printf("next_stop_i: %d/%d" % (next_stop_i, buses_struc_list[i].total_stops))
      // Check if the next stop is the last one
      if((next_stop_i >= bpa[i].total_stops) ||
        (next_stop_i < 0))
      {
        // Finish the bus and put in the rest position
        bpa[i].curr_stop = BUS_FINISHED;
        bpa[i].curr_pos = 0;
        continue;
      }

      // Look if the bus is inside the stop window of the next stop
      if(abs(pwq[next_stop_i].stop_pos - bpa[i].curr_pos)
          < STOP_BUS_WINDOW_DISTANCE){

        // Passing the stop, update last stop index
        bpa[i].last_stop_i = pwq[next_stop_i].stop_num;

        // Check if the stop is in the routes table to stop thee bus
        in_the_route = FALSE;
        for (int j = bpa[i].stops_num_i; j < bpa[i].total_stops; ++j) {
          if(pwq[next_stop_i].stop_num == bpa[i].stops_num[j]){
            bpa[i].stops_num_i = j;
            in_the_route = TRUE;
          }
        }

        // if this stop is in the stops table
        if(in_the_route){
          //printf("i: %d, Bus %d, in the stop: %d, pos %d\n", i,
          //  buses_struc_list[i].number,
          //  stops_queue_list[next_stop_i].stop_num,
          //  buses_struc_list[i].curr_pos);

          bpa[i].curr_stop = pwq[next_stop_i].stop_num;
          bpa[i].last_stop_pos = pwq[next_stop_i].stop_pos;
          bpa[i].in_the_stop = TRUE;
          bpa[i].in_the_stop_counter = BUS_STOPPING_TIME;
        }
      }

    } // End for each bus for(int i = 0; i < total_buses; ++i){

  } // End if(gid == 0){

#endif
}
