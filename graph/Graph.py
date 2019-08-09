from direct.showbase.ShowBase import ShowBase
from .Graph_bus_stop import Graph_bus_stop
from .Graph_bus import Graph_bus

from panda3d.core import TextNode
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
import logging
import time
import sys
import random


class Graph(DirectObject):
 
  def __init__(self, masivo, base):
    print("init")
    #ShowBase.__init__(self)
    self.base = base

    self.base.setBackgroundColor(0.1, 0.1, 0.1)  # Set the background to black
    #base.disableMouse()  # disable mouse control of the camera
    #camera.setPos(0, 0, 45)  # Set the camera position (X, Y, Z)
    #camera.setHpr(0, -90, 0)  # Set the camera orientation
    self.base.trackball.node().setPos(-86, 138, -24)
    self.base.trackball.node().setHpr(0, 40, 0)


    # Create Ambient Light
    ambientLight = AmbientLight('ambientLight')
    ambientLight.setColor((0.01, 0.01, 0.01, 1))
    ambientLightNP = render.attachNewNode(ambientLight)
    render.setLight(ambientLightNP)

    # Directional light 01
    directionalLight = DirectionalLight('directionalLight')
    directionalLight.setColor((2,  2, 2, 1))
    directionalLightNP = render.attachNewNode(directionalLight)
    # This light is facing backwards, towards the camera.
    directionalLightNP.setHpr(-45, -45, 0)
    render.setLight(directionalLightNP)

    # Load the cartesian plane
    self.plane = loader.loadModel("./graph/models/plane")
    self.plane.setPos(100,50,0)
    self.plane.reparentTo(render)

    self.bus_stop_list = []
    self.buses_list = []

    if "stops_list" in masivo:
      for stop in masivo["stops_list"]:
        bus_stop = Graph_bus_stop(stop.max_capacity, stop.possition, 10)
        bus_stop.set_pass(stop.pass_count())
        self.bus_stop_list.append(bus_stop)
    
    if "buses_list" in masivo:
      for bus in masivo["buses_list"]:
        bus = Graph_bus(bus.max_capacity, 0, 8)
        self.buses_list.append(bus)
        
    self.accept("escape", sys.exit)
    self.accept('spam',self.OnSpam)


  def OnSpam(self, masivo):
    
    #print(self.base.trackball.node().getPos())
    #print(self.base.trackball.node().getHpr())

    for i in range(0, len(self.bus_stop_list)):
      self.bus_stop_list[i].set_pass(masivo["stops_list"][i].pass_count())

    for i in range(0, len(self.buses_list)):
      self.buses_list[i].set_pos(masivo["buses_list"][i].current_possition, 8)
      self.buses_list[i].set_pass(masivo["buses_list"][i].pass_count())

def panda3d_run(masivo, base):
  w, h = 1900, 810
  props = WindowProperties() 
  props.setSize(w, h) 
  base.win.requestProperties(props) 

  app = Graph(masivo, base)
  base.run()

  



  