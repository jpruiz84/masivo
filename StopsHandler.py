import globalConstants
import logging
import csv
from Stop import Stop
import time
import numpy as np
import random
import pyopencl as cl
import pyopencl.array as cl_array


class StopsHandler:

  def __init__(self):

    print('load program from cl source file')
    f = open('tests/pyopencl/kernels_struct.cl', 'r', encoding='utf-8')
    kernels = ''.join(f.readlines())
    f.close()

    ocl_platforms = (platform.name
                     for platform in cl.get_platforms())
    print("\n".join(ocl_platforms))

    nvidia_platform = [platform
                       for platform in cl.get_platforms()
                       if platform.name == "NVIDIA CUDA"][0]

    nvidia_devices = nvidia_platform.get_devices()

    self.ctx = cl.Context(devices=nvidia_devices)
    self.queue = cl.CommandQueue(self.ctx)
    self.mf = cl.mem_flags
    self.prg = cl.Program(self.ctx, kernels).build()

    self.stops_list = []
    self.open_stops_file(globalConstants.ODM_FILE)

    self.pass_list = np.zeros(len(self.stops_list), globalConstants.spsl_type)
    self.pass_arrival_list = np.zeros(len(self.stops_list), globalConstants.spsl_type)
    self.pass_alight_list = np.zeros(len(self.stops_list), globalConstants.spsl_type)

    for i in range(len(self.stops_list)):
      self.stops_list[i].set_stop_lists(self.pass_list[i], self.pass_arrival_list[i], self.pass_alight_list[i])

    self.generate_pass_input()

    self.pass_list_g = cl_array.to_device(self.queue, self.pass_list)
    self.pass_arrival_list_g = cl_array.to_device(self.queue, self.pass_arrival_list)
    self.pass_alight_list_g = cl_array.to_device(self.queue, self.pass_alight_list)

    for i in range(len(self.stops_list)):
      self.stops_list[i].set_cl_lists(self.pass_list_g[i], self.pass_arrival_list_g[i], self.pass_alight_list_g[i])


  def get_stops_list(self):
    return self.stops_list

  def get_pass_list(self):
    return self.pass_list

  def get_pass_alight_list(self):
    return self.pass_alight_list

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

  def generate_pass_input(self):
    start_time = time.time()

    # For each destination
    for i in range(len(self.pass_list)):
      for j in range(len(self.pass_list[i]['spl'])):
        self.pass_arrival_list[i]['spl'][j]['status'] = globalConstants.PASS_STATUS_EMPTY_255

    # Calculate total pass in and input queue
    for i in range(len(self.stops_list)):
      logging.info("Generating pass input queue for stop name %s" % self.stops_list[i].name)
      # For each destination
      for key, val in self.stops_list[i].destination_vector.items():
        for j in range(val):

          k = self.pass_arrival_list[i]['last_empty']
          self.pass_arrival_list[i]['spl'][k]['pass_id'] = globalConstants.pass_num
          self.pass_arrival_list[i]['spl'][k]['orig_stop'] = int(self.stops_list[i].number)
          self.pass_arrival_list[i]['spl'][k]['dest_stop'] = int(key)
          self.pass_arrival_list[i]['spl'][k]['arrival_time'] = \
            random.randint(0, globalConstants.PASS_TOTAL_ARRIVAL_TIME)
          self.pass_arrival_list[i]['spl'][k]['status'] = globalConstants.PASS_STATUS_TO_ARRIVE
          self.pass_arrival_list[i]['total'] += 1
          self.pass_arrival_list[i]['last_empty'] += 1
          globalConstants.pass_num += 1

      # Sort items by arrival time ascending
      self.pass_arrival_list[i]['spl'].sort(order=['status', 'arrival_time'])
    end_time = time.time()
    print("generate_pass_input_queue stops time %d ms" % ((end_time - start_time)*1000))

  def runner(self, sim_time):

    if globalConstants.cl_enabled:
      np_stops_num = np.uint32(len(self.pass_list_g))
      np_pass_per_stop = np.uint32(globalConstants.STOP_MAX_PASS)
      np_sim_time = np.uint32(sim_time)

      evt = self.prg.move_pass(self.queue, (np_stops_num,), None,
                               self.pass_list_g.data, self.pass_arrival_list_g.data,
                               np_stops_num, np_pass_per_stop, np_sim_time)

      evt.wait()
      #np.array(self.pass_list_g[0].get(), dtype=self.spsl_type)['total']

    else:
      # For each stop
      for i in range(len(self.stops_list)):
        if self.pass_arrival_list[i]['total'] > 0:
          while True:
            # Check if the list is finished
            if self.pass_arrival_list[i]['w_index'] >= len(self.pass_arrival_list[i]['spl']):
              break

            # Check pass status
            if self.pass_arrival_list[i]['spl'][self.pass_arrival_list[i]['w_index']]['status'] \
                != globalConstants.PASS_STATUS_TO_ARRIVE:
              break

            # Check arrival time
            if sim_time < self.pass_arrival_list[i]['spl'][self.pass_arrival_list[i]['w_index']]['arrival_time']:
              break

            self.pass_list[i]['spl'][self.pass_list[i]['last_empty']] = \
              np.copy(self.pass_arrival_list[i]['spl'][self.pass_arrival_list[i]['w_index']])
            self.pass_list[i]['spl'][self.pass_list[i]['last_empty']]['status'] = globalConstants.PASS_STATUS_ARRIVED
            self.pass_list[i]['last_empty'] += 1
            self.pass_list[i]['total'] += 1

            self.pass_arrival_list[i]['spl'][self.pass_arrival_list[i]['w_index']]['status'] = \
              globalConstants.PASS_STATUS_EMPTY

            self.pass_arrival_list[i]['last_empty'] -= 1
            self.pass_arrival_list[i]['total'] -= 1
            self.pass_arrival_list[i]['w_index'] += 1





