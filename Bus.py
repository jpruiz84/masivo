import globalConstants
from struct import *
import logging
import copy


class Bus:

  def __init__(self, number, route):
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

    if route.dir == 'W-E':
      self.y_pos = 950
    else:
      self.y_pos = 1050
      self.travel_speed_m_s *= -1

  def set_list(self, pass_list):
    self.pass_list = pass_list

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
        self.pass_list['last_stop_i'] = self.route.stops_num_table.index(self.pass_list['curr_stop'])
        self.pass_list['curr_stop'] = globalConstants.BUS_TRAVELING

    # If I am not waiting in a stop, go ahead
    if not self.in_the_stop:
      self.current_position += self.travel_speed_m_s

    # Check if the bus have leave the current stop, if not, do not check for other stop
    if abs(self.current_stop.position - self.current_position) < globalConstants.STOP_BUS_WINDOW_DISTANCE:
      return

    # Check if the bus is at any stop
    for stop in stops_list:
      # Look if I am in the stop window
      if abs(stop.position - self.current_position) < globalConstants.STOP_BUS_WINDOW_DISTANCE:
        if stop.name in self.route.stops_table:
          logging.info("Bus %s, in the stop: %s, poss %d, is full: %s" % (
                       self.number, stop.name, self.current_position, str(self.is_full())))
          self.current_stop = stop
          self.pass_list['curr_stop'] = stop.number
          self.in_the_stop = True
          self.in_the_stop_counter = self.stopping_time
          break

  # Needs to be called each simulation second
  def runner(self, stops_list):

    # If waiting in the stop
    if self.in_the_stop:
      if self.current_stop.number in  self.remaining_stops_num:
        self.remaining_stops_num.remove(self.current_stop.number)

      # Only boarding if there is remaining stops
      if len(self.remaining_stops_num) > 0:
        # Boarding
        index = 0
        while index < self.current_stop.pass_count():
          if self.is_full():
            break
          pass_pack = self.current_stop.pass_to_bus(self, index)
          if pass_pack != "":
            self.pass_in(pass_pack)
            continue
          index += 1

      # Alight pass in the stop
      for pass_data in self.pass_queue:
        if pass_data['dest_stop'] == self.current_stop.number:
          logging.info('ALIGHT, pass %d from stop %d alighted in stop %d' %
                       (pass_data['pass_id'], pass_data['orig_stop'], pass_data['dest_stop']))
          self.current_stop.pass_alight(pass_data)
          self.pass_queue.remove(pass_data)

      # Check if we have to depart from the stop
      self.in_the_stop_counter -= 1
      if self.in_the_stop_counter == 0:
        self.in_the_stop = False

    # If I am not waiting in a stop, go ahead
    if not self.in_the_stop:
      self.current_position += self.travel_speed_m_s

    # Check if the bus have leave the last stop, if not, do not check for other stop
    if abs(self.current_stop.position - self.current_position) < globalConstants.STOP_BUS_WINDOW_DISTANCE:
      return

    # Check if the bus is at any stop
    for stop in stops_list:
      # Look if I am in the stop window
      if abs(stop.position - self.current_position) < globalConstants.STOP_BUS_WINDOW_DISTANCE:
        if stop.name in self.route.stops_table:
          logging.info("Bus %s, in the stop: %s, poss %d, is full: %s" % (
          self.number, stop.name, self.current_position, str(self.is_full())))
          self.current_stop = stop
          self.in_the_stop = True
          self.in_the_stop_counter = self.stopping_time
          break



