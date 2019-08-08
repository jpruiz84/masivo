class Bus:
  
  def __init__(self, id, time_offset, stop_list):
    self.id = id
    self.max_capacity = 100
    self.pass_queue = []
    self.travel_speed = 1          # m/s
    self.stopping_time = 30
    self.route_frequency = 10
    self.current_possition = 0
    self.stop_list = stop_list
    self.time_offset = time_offset

  def pass_in(self, pass_id):
    if(len(self.pass_queue) < self.max_capacity):
      self.pass_queue.append(pass_id)
      return True
    else:
      return False

  def pass_out(self):
    if(len(self.pass_queue)):
      return self.pass_queue.pop(0)
    else:
      return ""
    
  def pass_count(self):
    return len(self.pass_queue)

  def get_id(self):
    return self.id

  def update_possition(self, time):
    # Check if bus is at any stop
    for stop in self.stop_list:
      if stop.possition == self.current_possition:
        #print("In the stop: %s" % stop.id)

        for p in range(0, stop.pass_count()):
          self.pass_in(stop.pass_to_bus())
        
    self.current_possition = self.travel_speed*(time - self.time_offset)