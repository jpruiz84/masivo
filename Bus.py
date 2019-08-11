import globalConstants
from struct import *


class Bus:
  
  def __init__(self, id, time_offset, stop_list):
    self.id = id
    self.max_capacity = 1000
    self.pass_queue = []
    self.travel_speed_km_h = 40          # Km/h
    self.travel_speed_m_s = self.travel_speed_km_h*1000.0/3600.0          # Km/s
    self.stopping_time = 30
    self.route_frequency = 10
    self.current_position = 0
    self.stop_list = stop_list
    self.time_offset = time_offset
    self.lastStopName = ""
    self.in_the_stop = False
    self.in_the_stop_counter = 0
    self.current_stop = 0

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
    return len(self.pass_queue)

  def get_id(self):
    return self.id

  def is_full(self):
    if self.pass_count() >= self.max_capacity:
      return True
    else:
      return False

  # Needs to be called each simulation second
  def runner(self, time):

    # If I have not departed yet
    if time < self.time_offset:
      return

    # If waiting in the stop
    if self.in_the_stop:
      # Boarding
      for p in range(0, self.current_stop.pass_count()):
        if self.is_full():
          break
        pass_pack = self.current_stop.pass_to_bus()
        (alight_time, arrival_time, dest_stop, orig_stop, pass_id) = \
          unpack(globalConstants.PASS_DATA_FORMAT, pass_pack)
        print('BOARDING, Pass %d from stop %d into bus %s' % (pass_id, orig_stop, self.get_id()))
        self.pass_in(pass_pack)

      # Alight pass in the stop
      for pass_pack in self.pass_queue:
        (alight_time, arrival_time, dest_stop, orig_stop, pass_id) = \
          unpack(globalConstants.PASS_DATA_FORMAT, pass_pack)
        if dest_stop == self.current_stop.number:
          print('ALIGHT, [ass %d from stop %d alighted in stop %d' % (pass_id, orig_stop, dest_stop))
          self.current_stop.pass_alight(pass_pack)
          self.pass_queue.remove(pass_pack)

      # Check if we have to depart from the stop
      self.in_the_stop_counter -= 1
      if self.in_the_stop_counter == 0:
        self.in_the_stop = False
      return

    # If I am not waiting in a stop, go ahead
    if not self.in_the_stop:
      self.current_position += self.travel_speed_m_s

    # Check if the bus is at any stop
    for stop in self.stop_list:
      # Look if I am in the stop window
      if abs(stop.position - self.current_position) < globalConstants.STOP_BUS_WINDOW_DISTANCE:
        print("Bus %s, in the stop: %s, poss %d, is full: %s" % (
        self.id, stop.name, self.current_position, str(self.is_full())))
        self.current_stop = stop
        self.in_the_stop = True
        self.in_the_stop_counter = self.stopping_time
        break



