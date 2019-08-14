from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "window-title Masivo Public Transport Simulator")
loadPrcFileData("", "fullscreen 0") # Set to 1 for fullscreen
loadPrcFileData("", "win-size 1920 900")

from direct.showbase.ShowBase import ShowBase
from .GraphStop import GraphStop
from .GraphBus import GraphBus
from panda3d.core import *
import sys
from direct.task import Task


class Graph(ShowBase):

  def __init__(self, masivo):
    ShowBase.__init__(self)
    self.masivo = masivo

    base.setBackgroundColor(0.1, 0.1, 0.1)  # Set the background to black
    base.trackball.node().setPos(-835, 770, -570)   # To see only first 3 stops
    base.trackball.node().setHpr(0, 40, 0)
    base.trackball.node().setForwardScale(5)

    # Add the spinCameraTask procedure to the task manager.
    base.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    # Create Ambient Light
    ambient_light = AmbientLight('ambient_light')
    ambient_light_bright = 0.1
    ambient_light.setColor((ambient_light_bright, ambient_light_bright, ambient_light_bright, 1))
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

    # model for the camera to orbit along
    self.model = loader.loadModel('smiley')
    self.model.setScale(1, 1, 1)
    self.model.reparentTo(render)

    # Init lists for stops and buses
    self.bus_stop_list = []
    self.buses_list = []

    if "stops_list" in masivo:
      for stop in masivo["stops_list"]:
        bus_stop = GraphStop(stop)
        bus_stop.set_pass(stop.pass_count())
        self.bus_stop_list.append(bus_stop)

    if "buses_list" in masivo:
      for bus in masivo["buses_list"]:
        bus = GraphBus(bus.max_capacity, bus.current_position, bus.y_pos)
        self.buses_list.append(bus)

    self.accept("escape", sys.exit)

    base.taskMgr.add(self.update_simulation, "UpdateSimulationTask")

  # Define a procedure to move the camera.
  def spinCameraTask(self, task):
    if False:
      print(base.trackball.node().getPos())
      print(base.trackball.node().getHpr())

    (h, p, r) = self.camera.getHpr()
    self.camera.setHpr(h, p, 0)
    self.trackball.node().resetOriginHere()
    return Task.cont

  def update_simulation(self, task):
    # Update stops graphs
    for i in range(0, len(self.bus_stop_list)):
      self.bus_stop_list[i].set_pass(self.masivo["stops_list"][i].pass_count())
      self.bus_stop_list[i].set_alight(self.masivo["stops_list"][i].pass_alight_count(),
                                       self.masivo["stops_list"][i].expected_alight_pass)

    # Update buses
    for i in range(0, len(self.masivo["buses_list"])):
      # Check if there is a need to create new bus
      if i >= len(self.masivo["buses_list"]):
        break
      if len(self.buses_list) <= i:
        bus = GraphBus(self.masivo["buses_list"][i].max_capacity,
                       self.masivo["buses_list"][i].current_position, self.masivo["buses_list"][i].y_pos)
        self.buses_list.append(bus)

      if i >= len(self.masivo["buses_list"]):
        break
      # Update bus position and count
      self.buses_list[i].set_pos(self.masivo["buses_list"][i].current_position, self.masivo["buses_list"][i].y_pos)
      self.buses_list[i].set_pass(self.masivo["buses_list"][i].pass_count())

    return Task.cont

def panda3d_run(masivo):
  app = Graph(masivo)
  app.run()
