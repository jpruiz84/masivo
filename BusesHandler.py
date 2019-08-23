import globalConstants
import logging
from Route import Route
import csv
from Bus import Bus
import numpy as np


class BusesHandler:

  def __init__(self, stops_list, stops_pass_list, stops_alight_pass_list):
    self.buses_list = []
    self.finished_buses_list = []
    self.stops_list = stops_list
    self.stops_pass_list = stops_pass_list
    self.sap_list = stops_alight_pass_list
    self.routes_list = []

    self.bus_count = 0
    self.open_routes_file(globalConstants.ROUTES_FILE)

    self.bus_pass_lists = np.zeros(len(self.buses_list), dtype=globalConstants.bpsl_type)
    self.bl_head = 0
    self.bl_tail = 0


    # Init empty stops table
    for i in range(len(self.bus_pass_lists)):
      for j in range(len(self.bus_pass_lists[i]['stops_num'])):
        self.bus_pass_lists[i]['stops_num'][j] = globalConstants.EMPTY_STOP_NUMBER
      self.bus_pass_lists[i]['curr_stop'] = globalConstants.BUS_NOT_STARTED_STOP

    # Set the buses list
    for i in range(len(self.buses_list)):
      self.buses_list[i].set_list(self.bus_pass_lists[i])

    # Set in list the bus stops table
    for i in range(len(self.buses_list)):
      for j in range(len(self.buses_list[i].route.stops_num_table)):
        self.bus_pass_lists[i]['stops_num'][j] = self.buses_list[i].route.stops_num_table[j]
      self.bus_pass_lists[i]['total_stops'] = len(self.buses_list[i].route.stops_num_table)

  def get_buses_list(self):
    return self.buses_list

  def get_bus_pass_list(self):
    return self.bus_pass_lists

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
        bus = Bus(self.bus_count, route)
        self.bus_count += 1
        bus.start_time = route.time_offset + route.bus_counter*route.frequency
        route.bus_counter += 1
        self.buses_list.append(bus)

    logging.info("Total created buses %d" % len(self.buses_list))

  def create_bus(self, sim_time, route):
    bus = Bus(self.bus_count, route)
    self.bus_count += 1
    route.last_bus_time = sim_time - route.time_offset
    self.buses_list.append(bus)

    bus_pass = np.zeros(1, dtype=self.bus_pass_list_type)
    self.bus_pass_lists = np.vstack((self.bus_pass_lists, bus_pass))
    logging.info("Bus %d created with route %s", bus.number, bus.route.name)

  def runner(self, sim_time):

    # Update the bus position
    for bus in self.buses_list:
      # Check if start the bus
      if bus.current_stop == globalConstants.BUS_NOT_STARTED_STOP:
        if sim_time >= bus.start_time:
          bus.current_stop = bus.route.start_stop
          self.bus_pass_lists[bus.number]['curr_stop'] = bus.route.start_stop.number
          bus.current_position = bus.route.start_stop.x_pos
          logging.info("Starting bus %d with route %s, start time %d", bus.number, bus.route.name, bus.start_time)
          self.bl_head += 1
        continue

      bus.update_pos(self.stops_list)

    return

    # Boarding
    # For each bus
    for i in range(len(self.buses_list)):
      # If waiting in the stop
      if self.buses_list[i].in_the_stop:
        # Only boarding if there is remaining stops
        if len(self.buses_list[i].remaining_stops_num) > 0:
          # Boarding
          # For each pass in the current stop
          for j in range(len(self.stops_pass_list[self.buses_list[i].current_stop.number])):
            if self.stops_pass_list[self.buses_list[i].current_stop.number][j][
              'status'] == globalConstants.PASS_STATUS_ARRIVED:

              # Check if the passenger go to any remaining stops
              if self.stops_pass_list[self.buses_list[i].current_stop.number][j]['dest_stop'] in \
                      self.buses_list[i].remaining_stops_num:
                # Check next free space in the bus
                for k in range(len(self.bus_pass_lists[i])):
                  if self.bus_pass_lists[i][k]['status'] != globalConstants.PASS_STATUS_IN_BUS:
                    self.stops_pass_list[self.buses_list[i].current_stop.number][j]['status'] = \
                      globalConstants.PASS_STATUS_IN_BUS
                    self.bus_pass_lists[i][k] = np.copy(self.stops_pass_list[self.buses_list[i].current_stop.number][j])

                    logging.info('BOARDING, pass %d from stop %d into bus %s' %
                                 (self.stops_pass_list[self.buses_list[i].current_stop.number][j]['pass_id'],
                                  self.stops_pass_list[self.buses_list[i].current_stop.number][j]['orig_stop'],
                                  self.buses_list[i].get_number()))
                    break
    '''
    index = 0
    while index < self.buses_list[i].current_stop.pass_count():
      if self.is_full():
        break
      pass_pack = self.current_stop.pass_to_bus(self, index)
      if pass_pack != "":
        self.pass_in(pass_pack)
        continue
      index += 1
      '''

    # ALIGHTING
    # For each bus
    for i in range(len(self.buses_list)):
      # If waiting in the stop
      if self.buses_list[i].in_the_stop:
        # For each pass
        for j in range(len(self.bus_pass_lists[i])):
          if self.bus_pass_lists[i][j]['status'] == globalConstants.PASS_STATUS_IN_BUS:
            if self.bus_pass_lists[i][j]['dest_stop'] == self.buses_list[i].current_stop.number:
              for k in range(len(self.sap_list[self.buses_list[i].current_stop.number])):
                self.bus_pass_lists[i][j]['status'] = globalConstants.PASS_STATUS_ALIGHTED
                if self.sap_list[self.buses_list[i].current_stop.number][k]['status'] == globalConstants.PASS_STATUS_EMPTY_ZERO:
                  self.sap_list[self.buses_list[i].current_stop.number][k] = np.copy(self.bus_pass_lists[i][j])

                  logging.info('ALIGHT, pass %d from stop %d alighted in stop %d' %
                               (self.bus_pass_lists[i][j]['pass_id'],
                                self.bus_pass_lists[i][j]['orig_stop'],
                                self.bus_pass_lists[i][j]['dest_stop']))
                  #for p in self.sap_list[self.buses_list[i].current_stop.number]:
                  #  if p['status'] != globalConstants.PASS_STATUS_EMPTY_ZERO:
                  #    print(p)
                  break


        '''
        # Alight pass in the stop
        for pass_data in self.pass_queue:
          if pass_data['dest_stop'] == self.current_stop.number:
            logging.info('ALIGHT, pass %d from stop %d alighted in stop %d' %
                         (pass_data['pass_id'], pass_data['orig_stop'], pass_data['dest_stop']))
            self.current_stop.pass_alight(pass_data)
            self.pass_queue.remove(pass_data)
        '''