from Masivo import Masivo
from graph.Graph import Graph
from graph.Graph import panda3d_run
from direct.stdpy import threading
from direct.showbase.ShowBase import ShowBase
import time

class Masivo_runner(threading.Thread):
  def run(self):
    masivo.run()

base = ShowBase()
masivo = Masivo()
masivo_data = masivo.get_masivo_data()
Masivo_runner().start()

panda3d_run(masivo_data, base)



