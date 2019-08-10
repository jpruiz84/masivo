class Stop:
  
  def __init__(self, number, name, x_pos, y_pos, max_capacity):
    self.number = number
    self.name = name
    self.x_pos = x_pos
    self.y_pos = y_pos
    self.possition = x_pos   # TODO: delete later, for legacy compatibility 1D
    self.max_capacity = max_capacity
    self.total_pass_in = 0
    self.pass_id_num = 0

    self.pass_queue = []
    self.pass_out_list = []
    self.destination_vector = {}

  def pass_in(self, pass_id):
    if(len(self.pass_queue) < self.max_capacity):
      self.pass_queue.append(pass_id)
      return True
    else:
      return False

  def pass_to_bus(self):
    if(len(self.pass_queue)):
      return self.pass_queue.pop(0)
    else:
      return ""

  def pass_out(self, pass_id):
    self.pass_out_list.append(pass_id)

  def pass_count(self):
    return len(self.pass_queue)

  def pass_out_count(self):
    return len(self.pass_out_list)

  def calculate_total_pass_in(self):
    self.total_pass_in = 0
    for key, value in self.destination_vector.items():
      self.total_pass_in += value 

  # Needs to be called each simulation second
  def runner(self, time):
    if time != 0:
      return
    for i in range(0, self.total_pass_in):
      pass_id = ("p%02d_%s" % (self.pass_id_num, self.name))
      self.pass_id_num += 1
      self.pass_in(pass_id)

