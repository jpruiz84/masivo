import globalConstants

class GraphStop():
  def __init__(self, capacity, x_pos, y_pos):

    self.capacity = capacity
    self.x_pos = x_pos
    self.y_pos = y_pos
    self.scale = globalConstants.BUS_AND_STOPS_SCALE

    self.container = loader.loadModel("./graph/models/stop_base")
    self.container.setPos(self.x_pos, self.y_pos, 0)
    self.container.setScale(self.scale, self.scale, self.scale)
    self.container.reparentTo(render)

    self.indicator = loader.loadModel("./graph/models/stop_indicator")
    self.indicator.reparentTo(self.container)

    self.indicator_alight = loader.loadModel("./graph/models/stop_indicator_alight")
    self.indicator_alight.reparentTo(self.container)

    # print("Created Graph stop at: %f, %f" %(self.x_pos, self.y_pos))
      
  def set_pass(self, pass_num):
    if pass_num > self.capacity:
      pass_num = self.capacity

    self.indicator.setScale(1.0*pass_num/self.capacity,1,1)   
    x_pos = 1*0.25*(1-1.0*pass_num/self.capacity)
    self.indicator.setPos(x_pos, 0, 0)

  def set_alight(self, pass_alight_count, expected_pass_alight):
    if pass_alight_count > expected_pass_alight:
      pass_alight_count = expected_pass_alight

    self.indicator_alight.setScale(1, 1, 1.0 * pass_alight_count / expected_pass_alight)
    z_pos = 0.4 * (1 - 1.0 * pass_alight_count / expected_pass_alight)
    self.indicator_alight.setPos(0, 0, z_pos)