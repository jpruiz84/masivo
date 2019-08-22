from Masivo import Masivo
from graph.Graph import panda3d_run
from direct.stdpy import threading
import time

PANDA3D_ON = True


class MasivoRunner(threading.Thread):
  def run(self):
    time.sleep(2)
    masivo.run()


if PANDA3D_ON:
  masivo = Masivo()
  masivo_data = masivo.get_masivo_data()
  MasivoRunner().start()

  panda3d_run(masivo_data)

else:
  masivo = Masivo()
  masivo.run()
