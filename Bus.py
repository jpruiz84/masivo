STOP_BUS_WINDOW_DISTANCE = 10


class Bus:
  
  def __init__(self, id, time_offset, stop_list):
    self.id = id
    self.max_capacity = 200
    self.pass_queue = []
    self.travel_speed_km_h = 40          # Km/h
    self.travel_speed_m_s = self.travel_speed_km_h*1000.0/3600.0          # Km/s
    self.stopping_time = 30
    self.route_frequency = 10
    self.current_position = 0
    self.stop_list = stop_list
    self.time_offset = time_offset
    self.lastStopName = ""

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

  def runner(self, time):
    # Check if bus is at any stop
    for stop in self.stop_list:
      if self.lastStopName == stop.name:
        continue

      if abs(stop.position - self.current_position) < STOP_BUS_WINDOW_DISTANCE:
        for p in range(0, stop.pass_count()):
          if self.is_full():
            break
          self.pass_in(stop.pass_to_bus())
          print("Bus %s, in the stop: %s, poss %d, is full: %s" % (self.id, stop.name, self.current_position, str(self.is_full())))
        self.lastStopName = stop.name

    self.current_position = self.travel_speed_m_s *(time - self.time_offset)