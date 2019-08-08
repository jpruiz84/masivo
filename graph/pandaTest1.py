  rom direct.showbase.ShowBase import ShowBase
base = ShowBase()
from Bus_stop import Bus_stop
from Bus import Bus

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

class MyApp(DirectObject):
 
  def __init__(self):
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
    self.plane = loader.loadModel("models/plane")
    self.plane.setPos(100,50,0)
    self.plane.reparentTo(render)

    self.bus_stop_list = []
    for i in range (0, 10):
      for j in range (0, 9):
        bus_stop = Bus_stop(100, 10 + i*20, 10 + j*10)
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






def thread_function(name):
  h = 1
  inc = 1
  pos = 10
  while True:
    messenger.send('spam',[h, pos])
    time.sleep(0.01)
    h += inc
    pos += 0.01
    if(h >= 100):
      inc = -1
    if(h <= 0):
      inc = 1



format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")

logging.info("Main    : before creating thread")
x = threading.Thread(target=thread_function, args=(1,))
logging.info("Main    : before running thread")
x.start()
logging.info("Main    : wait for the thread to finish")
# x.join()
logging.info("Main    : all done")

w, h = 1440, 810
props = WindowProperties() 
props.setSize(w, h) 
base.win.requestProperties(props) 

print("d1")
app = MyApp()
#messenger.send('spam',['foo','bar'])
print("d2")

base.run()
