import globalConstants
import logging
import csv
from Stop import Stop


class StopsHandler:

  def __init__(self):
    self.stops_list = []
    self.open_stops_file(globalConstants.ODM_FILE)

  def get_stop_list(self):
    return self.stops_list

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

  def runner(self, sim_time):
    for stop in self.stops_list:
      stop.runner(sim_time)


