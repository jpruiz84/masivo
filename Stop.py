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
    self.pass_list = 0
    self.pass_arrival_list = 0
    self.pass_alight_list = 0

    self.pass_list_g = 0
    self.pass_arrival_list_g = 0
    self.pass_alight_list_g = 0

    self.destination_vector = {}
    self.expected_alight_pass = 0
    self.last_arrived_index = 0
    self.sap_index = 0

  def set_stop_lists(self, pass_list, pass_arrival_list, pass_alight_list):
    self.pass_list = pass_list
    self.pass_arrival_list = pass_arrival_list
    self.pass_alight_list = pass_alight_list

  def set_cl_lists(self, pass_list, pass_arrival_list, pass_alight_list):
    self.pass_list_g = pass_list
    self.pass_arrival_list_g = pass_arrival_list
    self.pass_alight_list_g = pass_alight_list

  def pass_count(self):
    if globalConstants.cl_enabled:
      return np.array(self.pass_list_g.get(), dtype=globalConstants.spsl_type)['total']
    else:
      return self.pass_list['total']

  def pass_alight_count(self):
    return 0

  def calculate_total_pass_in(self):
    self.total_pass_in = 0
    for key, value in self.destination_vector.items():
      self.total_pass_in += value

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

    self.pass_arrival_list_index = 0
    # For each destination
    for key, val in self.destination_vector.items():
      for i in range(0, val):
        self.pass_arrival_list[self.pass_arrival_list_index]['orig_stop'] = int(self.number)
        self.pass_arrival_list[self.pass_arrival_list_index]['dest_stop'] = int(key)
        self.pass_arrival_list[self.pass_arrival_list_index]['arrival_time'] = random.randint(0, globalConstants.PASS_TOTAL_ARRIVAL_TIME)
        self.pass_arrival_list[self.pass_arrival_list_index]['status'] = globalConstants.PASS_STATUS_TO_ARRIVE
        self.pass_arrival_list[self.pass_arrival_list_index]['pass_id'] = globalConstants.pass_num
        globalConstants.pass_num += 1

    # Sort items by arrival time ascending
    self.pass_arrival_list = np.sort(self.pass_arrival_list, order='arrival_time')

    return
