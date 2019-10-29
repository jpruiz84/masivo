from Stop import Stop
import sys
import time
import logging
import globalConstants
from BusesHandler import BusesHandler
from StopsHandler import StopsHandler
from graphs2d.Graphs2d import Graphs2d
import numpy as np
import results


class Masivo:
  def __init__(self):
    #logging.basicConfig(format='%(asctime)s %(message)s', level=globalConstants.LOGGING_LEVEL)
    logging.basicConfig(format='%(message)s', level=globalConstants.LOGGING_LEVEL)
    logging.info("Starting Masivo public transport simulator")

    # Init objects
    self.graphs2d = Graphs2d()

    # Init variables and lists
    self.pass_id_num = 0
    self.masivo_data = {}
    self.stops_list = []
    self.buses_list = []
    self.finished_buses_list = []
    self.speed_up = {"time": [], "speed_up": []}

    # Init stops
    self.stops_handler = StopsHandler()
    self.stops_list = self.stops_handler.get_stops_list()
    self.stops_pass_list = self.stops_handler.get_stops_list()
    self.stops_pass_alight_list = self.stops_handler.get_stops_alight_list()
    self.cl_queue = self.stops_handler.get_cl_queue()

    # Init buses
    self.buses_handler = BusesHandler(self.stops_list, self.cl_queue)
    self.buses_list = self.buses_handler.get_buses_list()
    self.buses_struc_list = self.buses_handler.get_bus_struc_list()
    self.buses_struc_list_g = self.buses_handler.get_bus_struc_list_g()

    # Set the buses_struc_list in the stops handler
    self.stops_handler.set_buses_struc_list(self.buses_struc_list)
    self.stops_handler.set_buses_struc_list_g(self.buses_struc_list_g)
    self.stops_handler.set_buses_handler(self.buses_handler)

    self.masivo_data["stops_list"] = self.stops_list
    self.masivo_data["buses_list"] = self.buses_list

  def run(self):
    total_start_time = time.time()
    for sim_time in range(0, globalConstants.END_SIM_TIME):
      start_time = time.time()

      if (sim_time % 10) == 0:
        sys.stdout.write("\rtime: %d  " % sim_time)
        sys.stdout.flush()

      if globalConstants.USE_PYOPENCL:
        self.stops_handler.runner_cl(sim_time)
      if globalConstants.USE_PYTHON_C:
        self.stops_handler.runner_c(sim_time)
      if globalConstants.USE_PYTHON:
        self.stops_handler.runner(sim_time)

      #self.buses_handler.runner(sim_time)

      if globalConstants.SIM_ACCEL_RATE > 0:
        while (time.time() - start_time) < (1 / globalConstants.SIM_ACCEL_RATE):
          pass

      self.speed_up["time"].append(sim_time)
      self.speed_up["speed_up"].append(1/(time.time() - start_time))

    total_end_time = time.time()

    print("\nAverage speed up: %d" % np.mean(self.speed_up["speed_up"]))
    print("Total time: %f s" % (total_end_time - total_start_time))

    # END SIMULATION, log results
    print("\n\nEND SIMULATION !!!!!")
    print("Total present buses: %d" % len(self.buses_list))
    print("Total finished buses: %d" % len(self.finished_buses_list))
    print("Total stops: %d" % len(self.masivo_data["stops_list"]))
    print("\n")

    print('\nBuses list:')
    for i in range(len(self.buses_struc_list)):
      print("Bus %s have %d pass, final pos %d" %
            (self.buses_list[i].number, self.buses_struc_list[i]['total'], self.buses_struc_list[i]['curr_pos']))

    print('\nStops list:')
    for stop in self.masivo_data["stops_list"]:
      print("Stop %s have %d/%d pass, and alighted %d/%d out" %
            (stop.name, stop.pass_count(), stop.total_pass_in, stop.pass_alight_count(), stop.expected_alight_pass))

    print("\nAverage speed up: %d" % np.mean(self.speed_up["speed_up"]))

    self.graphs2d.real_time_factor_graph(self.speed_up)
    self.graphs2d.save_speed_up_csv(self.speed_up)

    results.pass_alight(self.stops_pass_alight_list)

    if globalConstants.USE_PYTHON:
      print("Python Total time: %f s" % (total_end_time - total_start_time))
    elif globalConstants.USE_PYOPENCL:
      print("PyCL Total time: %f s" % (total_end_time - total_start_time))
    elif globalConstants.USE_PYTHON_C:
      print("PyC Total time: %f s" % (total_end_time - total_start_time))
    else:
      print("Total time: %f s" % (total_end_time - total_start_time))


  def get_masivo_data(self):
    return self.masivo_data
