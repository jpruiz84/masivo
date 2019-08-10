from direct.showbase.ShowBase import ShowBase
from .GraphStop import GraphStop
from .GraphBus import GraphBus
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
import sys


BUS_Y_POS = 950


class Graph(DirectObject):

  def __init__(self, masivo, base):
    print("init")
    # ShowBase.__init__(self)
    self.base = base

    self.base.setBackgroundColor(0.1, 0.1, 0.1)  # Set the background to black
    # base.disableMouse()  # disable mouse control of the camera
    # camera.setPos(0, 0, 45)  # Set the camera position (X, Y, Z)
    # camera.setHpr(0, -90, 0)  # Set the camera orientation
    self.base.trackball.node().setPos(-2100, 3500, -600)
    self.base.trackball.node().setHpr(0, 40, 0)
    self.base.trackball.node().setForwardScale(5)
    # self.base.trackball.node().getLens().lens.setNear(5.0)

    # Create Ambient Light
    ambient_light = AmbientLight('ambient_light')
    ambient_light.setColor((0.01, 0.01, 0.01, 1))
    ambient_light_np = render.attachNewNode(ambient_light)
    render.setLight(ambient_light_np)

    # Directional light 01
    directional_light = DirectionalLight('directional_light')
    directional_light.setColor((2, 2, 2, 1))
    directional_light_np = render.attachNewNode(directional_light)
    # This light is facing backwards, towards the camera.
    directional_light_np.setHpr(-45, -45, 0)
    render.setLight(directional_light_np)

    # Load the cartesian plane
    plane_scale = 1000
    self.plane = loader.loadModel("./graph/models/plane")
    self.plane.setPos(0, 0, 0)
    self.plane.setScale(plane_scale, plane_scale, plane_scale)
    self.plane.reparentTo(render)

    self.bus_stop_list = []
    self.buses_list = []

    if "stops_list" in masivo:
      for stop in masivo["stops_list"]:
        bus_stop = GraphStop(stop.max_capacity, stop.x_pos, stop.y_pos)
        bus_stop.set_pass(stop.pass_count())
        self.bus_stop_list.append(bus_stop)

    if "buses_list" in masivo:
      for bus in masivo["buses_list"]:
        bus = GraphBus(bus.max_capacity, 0, BUS_Y_POS)
        self.buses_list.append(bus)

    self.accept("escape", sys.exit)
    self.accept('spam', self.on_spam)

  def on_spam(self, masivo):
    if False:
      print(self.base.trackball.node().getPos())
      print(self.base.trackball.node().getHpr())


    for i in range(0, len(self.bus_stop_list)):
      self.bus_stop_list[i].set_pass(masivo["stops_list"][i].pass_count())

    for i in range(0, len(self.buses_list)):
      self.buses_list[i].set_pos(masivo["buses_list"][i].current_position, BUS_Y_POS)
      self.buses_list[i].set_pass(masivo["buses_list"][i].pass_count())


def panda3d_run(masivo, base):
  w, h = 1900, 810
  props = WindowProperties()
  props.setSize(w, h)
  base.win.requestProperties(props)

  app = Graph(masivo, base)
  base.run()
