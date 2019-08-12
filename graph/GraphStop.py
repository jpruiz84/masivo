import globalConstants
from pandac.PandaModules import TextNode, TextFont

class GraphStop():
  def __init__(self, stop):

    self.capacity = stop.max_capacity
    self.x_pos = stop.x_pos
    self.y_pos = stop.y_pos
    self.scale = globalConstants.BUS_AND_STOPS_SCALE

    self.container = loader.loadModel("./graph/models/stop_base")
    self.container.setPos(self.x_pos, self.y_pos, 0)
    self.container.setScale(self.scale, self.scale, self.scale)
    self.container.reparentTo(render)

    self.indicator = loader.loadModel("./graph/models/stop_indicator")
    self.indicator.reparentTo(self.container)

    self.indicator_alight = loader.loadModel("./graph/models/stop_indicator_alight")
    self.indicator_alight.reparentTo(self.container)

    text = TextNode('node name')
    text.setText(stop.name)
    text.setTextColor(0, 0, 0, 1)

    textNodePath = render2d.attachNewNode(text)
    textNodePath.setScale(1)
    textNodePath.setPos(1, -2, 0.1)
    textNodePath.setP(textNodePath, -90)
    textNodePath.reparentTo(self.container)

    # print("Created Graph stop at: %f, %f" %(self.x_pos, self.y_pos))
      
  def set_pass(self, pass_num):
    if pass_num > self.capacity:
      pass_num = self.capacity

    if pass_num == 0:
      self.indicator.hide()
    else:
      self.indicator.show()

    self.indicator.setScale(1.0*pass_num/self.capacity,1,1)   
    x_pos = 1*0.25*(1-1.0*pass_num/self.capacity)
    self.indicator.setPos(x_pos, 0, 0)

  def set_alight(self, pass_alight_count, expected_pass_alight):
    if pass_alight_count > expected_pass_alight:
      pass_alight_count = expected_pass_alight

    if pass_alight_count == 0:
      self.indicator_alight.hide()
    else:
      self.indicator_alight.show()

    self.indicator_alight.setScale(1, 1, 1.0 * pass_alight_count / expected_pass_alight)
    z_pos = 0.4 * (1 - 1.0 * pass_alight_count / expected_pass_alight)
    self.indicator_alight.setPos(0, 0, z_pos)