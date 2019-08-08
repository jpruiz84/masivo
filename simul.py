from Stop import Stop
from Bus import Bus

PASSENGER_INTERVAL = 10    # In seconds, every 50 seconds

STOPS_NUMBER = 100
STOPS_SPACCING = 100 

BUSES_NUMBER = 50
BUSES_TIME_SPACCING = 30

pass_id_num = 0

print("\fStarting simul")

stops_list = []
for i in range (0, STOPS_NUMBER):
  stop_id = ("s%02d" % i)
  stop = Stop(stop_id, i * STOPS_SPACCING)
  stops_list.append(stop)


buses_list = []
for i in range(0, BUSES_NUMBER):
  bus_id = ("b%02d" % i)
  bus = Bus(bus_id, BUSES_TIME_SPACCING * i, stops_list)
  buses_list.append(bus)

for i in range(0, 3600):
  #print("Time: %d" % i)
  for bus in buses_list:
    bus.update_possition(i)

  if (i % PASSENGER_INTERVAL == 0):
    for stop in stops_list:
      pass_id = ("p%02d" % pass_id_num)
      pass_id_num += 1
      r = stop.pass_in(pass_id)
      #print("Time %d, pass %s in to %s, %s" % (i, pass_id, stop.get_id(), str(r)))


for stop in stops_list:
  print("Stop %s have %d pass, and %d out" % (stop.get_id(), stop.pass_count(), stop.pass_out_count()))

for bus in buses_list:
  print("Bus %s have %d pass, final poss %d" % (bus.get_id(), bus.pass_count(), bus.current_possition))


print("End simulation")