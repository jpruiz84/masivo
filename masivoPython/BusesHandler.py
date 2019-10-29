import globalConstants
import logging
from Route import Route
import csv
from Bus import Bus
import numpy as np
import pyopencl as cl
import pyopencl.array as cl_array



class BusesHandler:

  def __init__(self, stops_list, cl_queue):
    self.buses_list = []
    self.finished_buses_list = []
    self.stops_list = stops_list
    self.routes_list = []
    self.cl_queue = cl_queue

    self.bus_count = 0
    self.open_routes_file(globalConstants.ROUTES_FILE)

    self.bus_struc_lists = np.zeros(len(self.buses_list), dtype=globalConstants.bpsl_type)
    self.bl_head = 0
    self.bl_tail = 0

    # Init empty stops table
    for i in range(len(self.bus_struc_lists)):
      for j in range(len(self.bus_struc_lists[i]['stops_num'])):
        self.bus_struc_lists[i]['stops_num'][j] = globalConstants.EMPTY_STOP_NUMBER
      self.bus_struc_lists[i]['curr_stop'] = globalConstants.BUS_NOT_STARTED_STOP

    # Set the buses list
    for i in range(len(self.buses_list)):
      self.buses_list[i].set_list(self.bus_struc_lists[i])

    # Set in list the bus stops table
    for i in range(len(self.buses_list)):
      for j in range(len(self.buses_list[i].route.stops_num_table)):
        self.bus_struc_lists[i]['stops_num'][j] = self.buses_list[i].route.stops_num_table[j]
      self.bus_struc_lists[i]['total_stops'] = len(self.buses_list[i].route.stops_num_table)

    self.bus_struc_lists_g = cl_array.to_device(self.cl_queue, self.bus_struc_lists)

    # Set the CL buses list
    for i in range(len(self.buses_list)):
      self.buses_list[i].set_cl_list(self.bus_struc_lists_g[i])

  def get_buses_list(self):
    return self.buses_list

  def get_bus_struc_list(self):
    return self.bus_struc_lists

  def get_bus_struc_list_g(self):
    return self.bus_struc_lists_g

  def open_routes_file(self, file_name):
    logging.info("Opening routes file: %s" % file_name)

    with open(file_name, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      # Read all routes info
      for row in reader:
        route = Route(row, self.stops_list)
        self.routes_list.append(route)

    # Create buses for each route
    for route in self.routes_list:
      logging.info("Creating %d buses for route %s" % (route.buses_total, route.name))
      for i in range(route.buses_total):
        bus = Bus(self.bus_count, route, self.stops_list)
        self.bus_count += 1
        bus.start_time = route.time_offset + route.bus_counter*route.frequency
        route.bus_counter += 1
        self.buses_list.append(bus)

    logging.info("Total created buses %d" % len(self.buses_list))

  def runner(self, sim_time):

    # Update the bus position
    for bus in self.buses_list:
      # Do not process finished buses
      if bus.bus_struc['curr_stop'] == globalConstants.BUS_FINISHED:
        continue

      # Check if start the bus
      if bus.bus_struc['curr_stop'] == globalConstants.BUS_NOT_STARTED_STOP:
        if sim_time >= bus.bus_struc['start_time']:
          bus.bus_struc['in_the_stop'] = True
          bus.bus_struc['curr_stop'] = bus.bus_struc['stops_num'][0]
          bus.bus_struc["last_stop_i"] = bus.bus_struc['stops_num'][0]
          bus.bus_struc["curr_pos"] = bus.bus_struc["start_pos"]
          bus.bus_struc['last_stop_pos'] = bus.bus_struc["curr_pos"]

          logging.info("Starting bus %d in stop %d start time %d",
                       bus.bus_struc["number"], bus.bus_struc['curr_stop'], bus.start_time)
          self.bl_head += 1
        continue

      bus.update_pos(self.stops_list)




