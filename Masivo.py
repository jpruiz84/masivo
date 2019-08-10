from Stop import Stop
from Bus import Bus
from direct.stdpy import thread
import time
import csv

PASSENGER_INTERVAL = 3    # In seconds, every 50 seconds

BUSES_NUMBER = 1000
BUSES_TIME_SPACCING = 15

SIMULATION_ACCELERATION_RATE = 100000

class Masivo():

  def __init__(self):

    print("Starting Masivo public transport simulator")

    # Init variables and lists

    self.pass_id_num = 0

    self.masivo_data = {}

    self.stops_list = []
    self.buses_list = []

    self.masivo_data["stops_list"] = self.stops_list
    self.masivo_data["buses_list"] = self.buses_list

    # Generate buses and bus stops

    self.open_stops_file("utils/odm1.csv")

    #for i in range (0, STOPS_NUMBER):
    #  stop_id = ("s%02d" % i)
    #  stop = Stop(stop_id, 10 + i * STOPS_SPACCING)
    #  self.stops_list.append(stop)


    for i in range(0, BUSES_NUMBER):
      bus_id = ("b%02d" % i)
      bus = Bus(bus_id, BUSES_TIME_SPACCING * i, self.stops_list)
      self.buses_list.append(bus)


  def run(self):
    
    for i in range(0, 3600):
      time.sleep(1.0/SIMULATION_ACCELERATION_RATE)
      print("Time: %d" % i)
      messenger.send('spam',[self.masivo_data])
      
      
      for bus in self.buses_list:
        bus.update_possition(i)

      for stop in self.stops_list:
        stop.runner(i)

    # Print simulation resutls

    for stop in self.masivo_data["stops_list"]:
      print("Stop %s have %d pass, and %d out" % (stop.name, stop.pass_count(), stop.pass_out_count()))

    for bus in self.masivo_data["buses_list"]:
      print("Bus %s have %d pass, final poss %d" % (bus.get_id(), bus.pass_count(), bus.current_possition))


    print("End simulation")

  def get_masivo_data(self):
    return self.masivo_data

  def open_stops_file(self, file_name):
    print("Opening stops file: %s" % file_name)
    with open(file_name, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      
      # Get stop first columns
      for row in reader:
        stop = Stop(int(row['stop_number']), row['stop_name'], 
        int(row['x_pos'])/1000.0, int(row['y_pos'])/1000.0, int(row['max_capacity']))
        
        self.stops_list.append(stop)

    # Get stop destination vector
    with open(file_name, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      # Rows have the destination of the stop users
      for row in reader:
        i = int(row['stop_number'])
        for stop in self.stops_list:
          self.stops_list[i].destination_vector[stop.name] = int(row[stop.name])

    
    for stop in self.stops_list:
      stop.calculate_total_pass_in()
    
    #print(self.stops_list[0].destination_vector)
    #print(self.stops_list[0].total_pass_in)

          