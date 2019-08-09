from Stop import Stop
from Bus import Bus
from direct.stdpy import thread
import time

PASSENGER_INTERVAL = 3    # In seconds, every 50 seconds

STOPS_NUMBER = 10
STOPS_SPACCING = 20 

BUSES_NUMBER = 100
BUSES_TIME_SPACCING = 100

SIMULATION_INTERVAL_MS = 100

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

    for i in range (0, STOPS_NUMBER):
      stop_id = ("s%02d" % i)
      stop = Stop(stop_id, 10 + i * STOPS_SPACCING)
      self.stops_list.append(stop)


    for i in range(0, BUSES_NUMBER):
      bus_id = ("b%02d" % i)
      bus = Bus(bus_id, BUSES_TIME_SPACCING * i, self.stops_list)
      self.buses_list.append(bus)


  def run(self):
    
    for i in range(0, 3600):
      time.sleep(SIMULATION_INTERVAL_MS/1000.0)
      #print("Time: %d" % i)
      messenger.send('spam',[self.masivo_data])
      
      
      for bus in self.buses_list:
        bus.update_possition(i)

      if (i % PASSENGER_INTERVAL == 0):
        for stop in self.stops_list:
          pass_id = ("p%02d" % self.pass_id_num)
          self.pass_id_num += 1
          r = stop.pass_in(pass_id)
          #print("Time %d, pass %s in to %s, %s" % (i, pass_id, stop.get_id(), str(r)))


    # Print simulation resutls

    for stop in self.masivo_data["stops_list"]:
      print("Stop %s have %d pass, and %d out" % (stop.get_id(), stop.pass_count(), stop.pass_out_count()))

    for bus in self.masivo_data["buses_list"]:
      print("Bus %s have %d pass, final poss %d" % (bus.get_id(), bus.pass_count(), bus.current_possition))


    print("End simulation")

  def get_masivo_data(self):
    return self.masivo_data

  