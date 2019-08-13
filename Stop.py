import globalConstants
import random
from struct import *
import logging
import binascii


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
    pass_pack = self.pass_queue[index]
    (alight_time, arrival_time, dest_stop, orig_stop, pass_id) = \
      unpack(globalConstants.PASS_DATA_FORMAT, pass_pack)
    if dest_stop in bus.remaining_stops_num:
      logging.info('BOARDING, pass %d from stop %d into bus %s' % (pass_id, orig_stop, bus.get_number()))
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

  def runner(self, sim_time):
    # Pass arrives to the stop
    index = 0
    while index < len(self.pass_arrival_list):
      (alight_time, arrival_time, dest_stop, orig_stop, pass_id) = \
        unpack(globalConstants.PASS_DATA_FORMAT, self.pass_arrival_list[index])
      if sim_time == arrival_time:
        self.pass_in(self.pass_arrival_list.pop(index))
        continue
      index += 1

  def generate_pass_input_queue(self):
    # logging.info("\nStop name %s" % self.name)
    # logging.info(self.destination_vector)
    for key, val in self.destination_vector.items():
      for i in range(0, val):
        orig_stop = int(self.number)
        dest_stop = int(key)
        arrival_time = random.randint(0, globalConstants.PASS_TOTAL_ARRIVAL_TIME)
        alight_time = 0
        pass_id = globalConstants.pass_num
        globalConstants.pass_num += 1
        pass_packed_data = pack(globalConstants.PASS_DATA_FORMAT,
                                alight_time, arrival_time, dest_stop, orig_stop, pass_id)
        # logging.info("pass_id %d \torig_stop %d \tdest_stop %d \tarrival_time %d \t alight_time %d" %
        #      (pass_id, orig_stop, dest_stop, arrival_time, alight_time))
        # logging.info(binascii.b2a_hex(pass_packed_data))
        self.pass_arrival_list.append(pass_packed_data)

    return
