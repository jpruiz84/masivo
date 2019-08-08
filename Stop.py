class Stop:
  
  def __init__(self, id, possition):
    self.id = id
    self.max_capacity = 200
    self.pass_queue = []
    self.possition = possition
    self.pass_out_list = []

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


  def get_id(self):
    return self.id