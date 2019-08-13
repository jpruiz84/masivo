import globalConstants
import logging
from Route import Route
import csv
from Bus import Bus


class BusesHandler:

  def __init__(self, stops_list):
    self.buses_list = []
    self.buses_list
    self.stops_list = stops_list
    self.routes_list = []

    self.open_routes_file(globalConstants.ROUTES_FILE)
    self.bus_count = 0

  def get_buses_list(self):
    return self.buses_list

  def open_routes_file(self, file_name):
    logging.info("Opening routes file: %s" % file_name)

    with open(file_name, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      # Read all routes info
      for row in reader:
        route = Route(row, self.stops_list)
        self.routes_list.append(route)

  def runner(self, sim_time):

    # Check for buses creation
    for route in self.routes_list:
      # Check if we need to create a new bus
      if (route.last_bus_time + route.frequency) <= (sim_time - route.time_offset):
        bus = Bus(self.bus_count, route)
        self.bus_count += 1
        route.last_bus_time = sim_time - route.time_offset
        self.buses_list.append(bus)
        logging.info("Bus %d created with route %s", bus.number, bus.route.name)

    for bus in self.buses_list:
      bus.runner(self.stops_list)
