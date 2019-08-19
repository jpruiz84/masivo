import globalConstants
import random
from struct import *
import logging
import numpy as np
from sys import getsizeof

class Stop:

  def __init__(self, number, name, x_pos, y_pos, max_capacity):
    self.number = number
    self.name = name
    self.x_pos = x_pos
    self.y_pos = y_pos
    self.position = x_pos  # TODO: delete later, for legacy compatibility 1D
    self.max_capacity = max_capacity
    self.total_pass_in = 0
    self.pass_id_num = 0

    self.pass_queue = []
    self.pass_alight_list = []
    self.destination_vector = {}
    self.pass_arrival_list = []
    self.expected_alight_pass = 0

  def pass_in(self, pass_id):
    if len(self.pass_queue) < self.max_capacity:
      self.pass_queue.append(pass_id)
      return True
    else:
      return False

  def pass_to_bus(self, bus, index):
    if not len(self.pass_queue):
      return ""

    # Boarding pass in the stop
    pass_data = self.pass_queue[index]
    if pass_data['dest_stop'] in bus.remaining_stops_num:
      logging.info('BOARDING, pass %d from stop %d into bus %s' %
                   (pass_data['pass_id'], pass_data['orig_stop'], bus.get_number()))
      return self.pass_queue.pop(index)

    return ""

  def pass_alight(self, pass_id):
    self.pass_alight_list.append(pass_id)

  def pass_count(self):
    return len(self.pass_queue)

  def pass_alight_count(self):
    return len(self.pass_alight_list)

  def calculate_total_pass_in(self):
    self.total_pass_in = 0
    for key, value in self.destination_vector.items():
      self.total_pass_in += value

      # Needs to be called each simulation second

  @staticmethod
  def get_pass_arrival_time(pass_pack):
    (alight_time, arrival_time, dest_stop, orig_stop, pass_id) = \
      unpack(globalConstants.PASS_DATA_FORMAT, pass_pack)
    return arrival_time

  def runner(self, sim_time):
    # Pass arrives to the stop
    if len(self.pass_arrival_list) > 0:
      while sim_time == self.pass_arrival_list[0]['arrival_time']:
        self.pass_in(self.pass_arrival_list.pop(0))
        if len(self.pass_arrival_list) == 0:
          break

  def generate_pass_input_queue(self):
    logging.info("Generating pass input queue for stop name %s" % self.name)

    # For each destination
    for key, val in self.destination_vector.items():
      for i in range(0, val):
        pass_data = np.zeros(1, globalConstants.PASS_TYPE)
        pass_data['orig_stop'] = int(self.number)
        pass_data['dest_stop'] = int(key)
        pass_data['arrival_time'] = random.randint(0, globalConstants.PASS_TOTAL_ARRIVAL_TIME)
        pass_data['status'] = globalConstants.PASS_STATUS_TO_ARRIVE
        pass_data['pass_id'] = random.randint(0, globalConstants.PASS_TOTAL_ARRIVAL_TIME)
        globalConstants.pass_num += 1
        self.pass_arrival_list.append(pass_data)

    # Sort items by arrival time ascending
    self.pass_arrival_list.sort(key=lambda x: x['arrival_time'])

    return
