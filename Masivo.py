from Stop import Stop
import sys
import time
import csv
import logging
import globalConstants
from BusesHandler import BusesHandler
from StopsHandler import StopsHandler
from graphs2d.Graphs2d import Graphs2d
import numpy as np


SIMULATION_ACCELERATION_RATE = 0


class Masivo:

  def __init__(self):
    logging.basicConfig(format='%(asctime)s %(message)s', level=globalConstants.LOGGING_LEVEL)
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
    self.stops_pass_list = self.stops_handler.get_pass_list()
    self.stops_pass_alight_list = self.stops_handler.get_pass_alight_list()

    # Init buses
    #self.buses_handler = BusesHandler(self.stops_list, self.stops_pass_list, self.stops_alight_pass_list)
    #self.buses_list = self.buses_handler.get_buses_list()
    #self.finished_buses_list = self.buses_handler.get_finished_buses_list()

    self.masivo_data["stops_list"] = self.stops_list
    self.masivo_data["buses_list"] = self.buses_list

  def run(self):
    total_start_time = time.time()
    for sim_time in range(0, 6000):
      start_time = time.time()

      if (sim_time % 10) == 0:
        sys.stdout.write("\rtime: %d  " % sim_time)
        sys.stdout.flush()

      self.stops_handler.runner(sim_time)
      #self.buses_handler.runner(sim_time)

      if SIMULATION_ACCELERATION_RATE > 0:
        while (time.time() - start_time) < (1 / SIMULATION_ACCELERATION_RATE):
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
    print("\n\n")
    for stop in self.masivo_data["stops_list"]:
      print("Stop %s have %d/%d pass, and %d/%d out" % (stop.name, stop.pass_count(), stop.total_pass_in,
                                                        stop.pass_alight_count(), stop.expected_alight_pass))
    for bus in self.finished_buses_list:
      print("Present Bus %s have %d pass, final poss %d" % (bus.get_number(), bus.pass_count(), bus.current_position))

    for bus in self.finished_buses_list:
      print("Finished bus %s have %d pass, final poss %d" % (bus.get_number(), bus.pass_count(), bus.current_position))

    print("\nAverage speed up: %d" % np.mean(self.speed_up["speed_up"]))
    print("Total time: %f" % (total_end_time - total_start_time))
    self.graphs2d.speed_up(self.speed_up)
    self.graphs2d.save_speed_up_csv(self.speed_up)

  def get_masivo_data(self):
    return self.masivo_data
