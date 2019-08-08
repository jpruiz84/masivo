from direct.showbase.ShowBase import ShowBase
from .Bus_stop import Bus_stop
from .Bus import Bus

from panda3d.core import TextNode
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
import logging
import threading
import time
import sys
import random


class Graph(DirectObject):
 
  def __init__(self, masivo):
    #ShowBase.__init__(self)

    base.setBackgroundColor(0, 0, 0)  # Set the background to black
    #base.disableMouse()  # disable mouse control of the camera
    #camera.setPos(0, 0, 45)  # Set the camera position (X, Y, Z)
    #camera.setHpr(0, -90, 0)  # Set the camera orientation
    base.trackball.node().setPos(-70, 200, -24)
    base.trackball.node().setHpr(0, 40, 0)


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

    for stop in masivo["stops_list"]:
      bus_stop = Bus_stop(stop.max_capacity, 10 + stop.possition, 10)
      bus_stop.set_pass(stop.pass_count())
      self.bus_stop_list.append(bus_stop)
    
    self.bus = Bus(50, 10, 11)
        
    
    self.accept("escape", sys.exit)
    self.accept('spam',self.OnSpam)


  def OnSpam(self, h, pos):
    #print h
    self.bus_stop_list[0].set_pass(h)
    self.bus.set_pos(pos, 11)
    self.bus.set_pass(h)
    #print base.trackball.node().getPos()
    #print base.trackball.node().getHpr()

def panda3d_runner(masivo):
  base = ShowBase()
  w, h = 1440, 810
  props = WindowProperties() 
  props.setSize(w, h) 
  base.win.requestProperties(props) 

  app = Graph(masivo)
  base.run()


  