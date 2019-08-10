class GraphStop():
  def __init__(self, capacity, x_pos, y_pos):

    self.capacity = capacity
    self.x_pos = x_pos
    self.y_pos = y_pos
    self.scale = 20

    self.container = loader.loadModel("./graph/models/stop_base")
    self.container.setPos(self.x_pos, self.y_pos, 0)
    self.container.setScale(self.scale, self.scale, self.scale)
    self.container.reparentTo(render)

    self.indicator = loader.loadModel("./graph/models/stop_indicator")
    self.indicator.setPos(0,0,0)
    self.indicator.setScale(self.scale, self.scale, self.scale)
    self.indicator.reparentTo(self.container)
    #print("Created Graph stop at: %f, %f" %(self.x_pos, self.y_pos))
      
  def set_pass(self, pass_num):
    if pass_num > self.capacity:
      pass_num = self.capacity

    self.indicator.setScale(1.0*pass_num/self.capacity,1,1)   
    x_pos = 1.25*0.25*(1-1.0*pass_num/self.capacity)
    self.indicator.setPos(x_pos, 0, 0)