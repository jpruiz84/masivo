from Masivo import Masivo
from graph.Graph import panda3d_run
from direct.stdpy import threading
import time
import globalConstants
import argparse

parser = argparse.ArgumentParser(description="Run Masivo parallel traffic simulation")
parser.add_argument("-m", "--max_cu", type=int, default=0,
                    help="Defines the max OpenCL compute units to use, defautl 0 unlimited.")
# Parse arguments
args = parser.parse_args()

globalConstants.LIMIT_MAX_CPUS = args.max_cu

class MasivoRunner(threading.Thread):
    def run(self):
        time.sleep(2)
        masivo.run()


if globalConstants.PANDA_3D_ENABLED:
    masivo = Masivo()
    masivo_data = masivo.get_masivo_data()
    MasivoRunner().start()

    panda3d_run(masivo_data)

else:
    masivo = Masivo()
    masivo.run()
