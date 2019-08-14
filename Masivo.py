from Stop import Stop
import sys
import time
import csv
import logging
import globalConstants
from BusesHandler import BusesHandler
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
    self.open_stops_file(globalConstants.ODM_FILE)

    # Init buses
    self.buses_handler = BusesHandler(self.stops_list)
    self.buses_list = self.buses_handler.get_buses_list()
    self.finished_buses_list = self.buses_handler.get_finished_buses_list()

    self.masivo_data["stops_list"] = self.stops_list
    self.masivo_data["buses_list"] = self.buses_list

  def run(self):
    for sim_time in range(0, 6000):
      start_time = time.time()



      if (sim_time % 10) == 0:
        sys.stdout.write("\rtime: %d  " % sim_time)
        sys.stdout.flush()

      for stop in self.stops_list:
        stop.runner(sim_time)

      self.buses_handler.runner(sim_time)

      if SIMULATION_ACCELERATION_RATE > 0:
        while (time.time() - start_time) < (1 / SIMULATION_ACCELERATION_RATE):
          pass


      self.speed_up["time"].append(sim_time)
      self.speed_up["speed_up"].append(1/(time.time() - start_time))

    print("Average speed up: %d" % np.mean(self.speed_up["speed_up"]))
    self.graphs2d.speed_up(self.speed_up)

    # END SIMULATION, log results
    print("\n\nEND SIMULATION !!!!!")
    print("Total present buses: %d" % len(self.buses_list))
    print("Total finished buses: %d" % len(self.finished_buses_list))
    print("Total stops: %d" % len(self.masivo_data["stops_list"]))
    print("\n\n")
    for stop in self.masivo_data["stops_list"]:
      print("Stop %s have %d/%d pass, and %d/%d out" % (stop.name, stop.pass_count(), len(stop.pass_arrival_list),
                                                        stop.pass_alight_count(), stop.expected_alight_pass))
    for bus in self.finished_buses_list:
      print("Present Bus %s have %d pass, final poss %d" % (bus.get_number(), bus.pass_count(), bus.current_position))

    for bus in self.finished_buses_list:
      print("Finished bus %s have %d pass, final poss %d" % (bus.get_number(), bus.pass_count(), bus.current_position))


  def get_masivo_data(self):
    return self.masivo_data

  def open_stops_file(self, file_name):
    logging.info("Opening stops file: %s" % file_name)

    # Get the stops number, name, poss and max capacity
    with open(file_name, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      # Get stop first columns
      for row in reader:
        stop = Stop(int(row['stop_number']), row['stop_name'],
                    int(row['x_pos']), int(row['y_pos']), int(row['max_capacity']))
        self.stops_list.append(stop)
        globalConstants.stops_name_to_num[row['stop_name']] = int(row['stop_number'])

    # Get stop destination vector
    with open(file_name, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      # Rows have the destinations of the stop users
      for row in reader:
        i = int(row['stop_number'])
        for stop in self.stops_list:
          self.stops_list[i].destination_vector[stop.number] = int(row[stop.name])
          self.stops_list[stop.number].expected_alight_pass += int(row[stop.name])

    # Calculate total pass in and input queue
    for stop in self.stops_list:
      stop.calculate_total_pass_in()
      stop.generate_pass_input_queue()

    # logging.info(self.stops_list[0].destination_vector)
    # logging.info(self.stops_list[0].total_pass_in)
    # logging.info(self.stops_list[0].expected_alight_pass)
