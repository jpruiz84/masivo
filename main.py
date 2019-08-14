from Masivo import Masivo
from graph.Graph import panda3d_run
from direct.stdpy import threading
import time


class MasivoRunner(threading.Thread):
  def run(self):
    time.sleep(2)
    masivo.run()


masivo = Masivo()
masivo_data = masivo.get_masivo_data()
MasivoRunner().start()

panda3d_run(masivo_data)
