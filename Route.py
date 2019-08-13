import globalConstants
import logging


class Route:

  def __init__(self, csv_row):
    self.number = int(csv_row['route_number'])
    self.name = csv_row['route_name']
    self.frequency = int(csv_row['route_frequency'])    # Interval in seconds
    self.dir = csv_row['route_dir']
    self.notes = csv_row['route_notes']
    self.stops_table = [x.strip() for x in csv_row['route_stops_table'].split(',')]

    self.stops_num_table = []
    for stop_name in self.stops_table:
      self.stops_num_table.append(globalConstants.stops_name_to_num[stop_name])

    self.last_bus_time = 0
    self.time_offset = int(csv_row['route_offset'])

