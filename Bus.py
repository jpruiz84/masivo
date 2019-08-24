import globalConstants
import numpy as np
import logging
import copy


class Bus:

  def __init__(self, number, route, stops_list):
    self.number = number
    self.route = route
    self.max_capacity = globalConstants.BUS_MAX_PASS
    self.pass_queue = []
    self.travel_speed_km_h = 40          # Km/h
    self.travel_speed_m_s = self.travel_speed_km_h*1000.0/3600.0          # Km/s
    self.stopping_time = 10
    self.current_position = 0
    self.in_the_stop = True
    self.in_the_stop_counter = self.stopping_time
    self.current_stop = globalConstants.BUS_NOT_STARTED_STOP
    self.remaining_stops_num = copy.copy(self.route.stops_num_table)
    self.start_time = 0
    self.pass_list = 0
    self.pass_list_g = 0
    self.stop_inc = 1
    self.total_stops = len(stops_list)
    self.stop_index = 0

    if route.dir == 'W-E':
      self.y_pos = 950
      self.stop_inc = 1
      self.last_stop_index = 0
    else:
      self.y_pos = 1050
      self.travel_speed_m_s *= -1
      self.stop_inc = -1
      self.last_stop_index = self.total_stops - 1

  def set_list(self, pass_list):
    self.pass_list = pass_list

  def set_cl_list(self, pass_list_g):
    self.pass_list_g = pass_list_g

  def pass_in(self, pass_id):
    if len(self.pass_queue) < self.max_capacity:
      self.pass_queue.append(pass_id)
      return True
    else:
      return False

  def pass_out(self):
    if len(self.pass_queue):
      return self.pass_queue.pop(0)
    else:
      return ""
    
  def pass_count(self):
    if globalConstants.cl_enabled:
      return np.array(self.pass_list_g.get(), dtype=globalConstants.bpsl_type)['total']
    else:
      return self.pass_list['total']

  def get_number(self):
    return self.number

  def is_full(self):
    if self.pass_count() >= self.max_capacity:
      return True
    else:
      return False

  def is_finished(self):
    if not self.in_the_stop:
      if len(self.remaining_stops_num) == 0:
        logging.info("Bus %d is finished" % self.number)
        return True
    return False

  def update_pos(self, stops_list):
    # If waiting in the stop
    if self.in_the_stop:
      # Remove the current stop for remaining stops
      if self.current_stop.number in self.remaining_stops_num:
        self.remaining_stops_num.remove(self.current_stop.number)

      # Check if we have to depart from the stop
      self.in_the_stop_counter -= 1
      if self.in_the_stop_counter == 0:
        self.in_the_stop = False
        if self.pass_list['curr_stop'] in self.route.stops_num_table:
          self.pass_list['last_stop_i'] = self.route.stops_num_table.index(self.pass_list['curr_stop'])
        self.pass_list['curr_stop'] = globalConstants.BUS_TRAVELING

        if globalConstants.cl_enabled:
          bus_g = np.array(self.pass_list_g.get(), dtype=globalConstants.bpsl_type)
          bus_g['last_stop_i'] = self.pass_list['last_stop_i']
          bus_g['curr_stop'] = globalConstants.BUS_TRAVELING
          self.pass_list_g.set(bus_g)

      return

    # If I am not waiting in a stop, go ahead
    if not self.in_the_stop:
      self.current_position += self.travel_speed_m_s

    # Check if the bus have leave the current stop, if not, do not check for other stop
    if abs(self.current_stop.position - self.current_position) < globalConstants.STOP_BUS_WINDOW_DISTANCE:
      return

    # Check if the bus is at any stop
    stop = stops_list[self.last_stop_index + self.stop_inc]
    # Look if I am in the stop window
    if abs(stop.position - self.current_position) < globalConstants.STOP_BUS_WINDOW_DISTANCE:
      self.last_stop_index = stop.number
      if stop.name in self.route.stops_table:
        logging.info("Bus %s, in the stop: %s, poss %d, is full: %s" % (
                     self.number, stop.name, self.current_position, str(self.is_full())))
        self.current_stop = stop
        self.pass_list['curr_stop'] = stop.number
        if globalConstants.cl_enabled:
          bus_g = np.array(self.pass_list_g.get(), dtype=globalConstants.bpsl_type)
          bus_g['curr_stop'] = stop.number
          self.pass_list_g.set(bus_g)

        self.in_the_stop = True
        self.in_the_stop_counter = self.stopping_time




