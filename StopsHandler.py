import globalConstants
import logging
import csv
from Stop import Stop
import time
import numpy as np
import random
import pyopencl as cl
import pyopencl.array as cl_array
import ctypes


class StopsHandler:

    def __init__(self):

        print('Load program from cl source file')
        f = open('c_code/kernels_struct.c', 'r', encoding='utf-8')
        kernels = ''.join(f.readlines())
        f.close()

        ocl_platforms = (platform.name
                         for platform in cl.get_platforms())
        # print("\n".join(ocl_platforms))

        cl_platform = cl.get_platforms()[-1]
        cl_devices = cl_platform.get_devices()

        if globalConstants.USE_PYOPENCL:
            for i, dev in enumerate(cl_devices):
                print('OpenCL device[%d]: %s, %s, max_cu: %d ' % (i, dev.name, dev.vendor, dev.max_compute_units))
                globalConstants.results['OpenCL_device_name'] = \
                    '"OpenCL device[%d]: %s, %s, max_cu: %d"' % (i, dev.name, dev.vendor, dev.max_compute_units)

        if globalConstants.LIMIT_MAX_CPUS > 0:
        # emulate multiple devices
            cl_devices = cl_devices[0].create_sub_devices(
                [cl.device_partition_property.BY_COUNTS, globalConstants.LIMIT_MAX_CPUS])

            for i, dev in enumerate(cl_devices):
                print('Emulated OpenCL device[%d]: %s, %s, max_cu: %d ' % (i, dev.name, dev.vendor, dev.max_compute_units))
                globalConstants.results['OpenCL_device_name'] = \
                    '"Emulated OpenCL device[%d]: %s, %s, max_cu: %d"' % (i, dev.name, dev.vendor, dev.max_compute_units)

        print()
        self.ctx = cl.Context(devices=cl_devices)
        self.queue = cl.CommandQueue(self.ctx)
        self.mf = cl.mem_flags
        self.prg = cl.Program(self.ctx, kernels).build()
        self.knl = self.prg.masivo_runner
        self.np_total_stops = 0

        self.buses_struc_list = 0
        self.buses_handler = 0

        self.grand_total_passengers = 0

        self.stops_object_list = []
        self.open_stops_file(globalConstants.ODM_FILE)

        self.stops_queue_list = np.zeros(len(self.stops_object_list), globalConstants.spsl_type)
        self.stops_arrival_list = np.zeros(len(self.stops_object_list), globalConstants.spsl_type)
        self.stops_alight_list = np.zeros(len(self.stops_object_list), globalConstants.spsl_type)
        self.buses_struc_list_g = 0

        for i in range(len(self.stops_object_list)):
            self.stops_queue_list[i]['stop_num'] = self.stops_object_list[i].number

        for i in range(len(self.stops_object_list)):
            self.stops_object_list[i].set_stop_lists(self.stops_queue_list[i], self.stops_arrival_list[i],
                                                     self.stops_alight_list[i])

        self.generate_pass_input()

        self.stops_queue_list_g = cl_array.to_device(self.queue, self.stops_queue_list)
        self.stops_arrival_list_g = cl_array.to_device(self.queue, self.stops_arrival_list)
        self.stops_alight_list_g = cl_array.to_device(self.queue, self.stops_alight_list)

        for i in range(len(self.stops_object_list)):
            self.stops_object_list[i].set_cl_lists(self.stops_queue_list_g[i], self.stops_arrival_list_g[i],
                                                   self.stops_alight_list_g[i])

    def get_cl_queue(self):
        return self.queue

    def get_stops_list(self):
        return self.stops_object_list

    def get_stops_arrival_list(self):
        if globalConstants.cl_enabled:
            return np.array(self.stops_arrival_list_g.get(), dtype=globalConstants.spsl_type)
        else:
            return self.stops_arrival_list

    def get_stops_queue_list(self):
        if globalConstants.cl_enabled:
            return np.array(self.stops_queue_list_g.get(), dtype=globalConstants.spsl_type)
        else:
            return self.stops_queue_list

    def get_stops_alight_list(self):
        if globalConstants.cl_enabled:
            return np.array(self.stops_alight_list_g.get(), dtype=globalConstants.spsl_type)
        else:
            return self.stops_alight_list

    def set_buses_struc_list(self, buses_struc_list):
        self.buses_struc_list = buses_struc_list

    def set_buses_struc_list_g(self, buses_struc_list_g):
        self.buses_struc_list_g = buses_struc_list_g

    def set_buses_handler(self, buses_handler):
        self.buses_handler = buses_handler

    def open_stops_file(self, file_name):
        logging.info("Opening stops file: %s" % file_name)

        # Get the stops number, name, poss and max capacity
        with open(file_name, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            # Get stop first columns
            for row in reader:
                stop = Stop(int(row['stop_number']), row['stop_name'],
                            int(row['x_pos']), int(row['y_pos']), int(row['max_capacity']))
                self.stops_object_list.append(stop)
                globalConstants.stops_name_to_num[row['stop_name']] = int(row['stop_number'])

        # Get stop destination vector
        with open(file_name, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            # Rows have the destinations of the users' stops
            for row in reader:
                i = int(row['stop_number'])
                self.stops_object_list[i].destination_vector = np.zeros(len(self.stops_object_list),
                                                                        globalConstants.dest_vec_type)
                for stop in self.stops_object_list:
                    self.stops_object_list[i].destination_vector[stop.number]['dest_total'] = int(row[stop.name])
                    self.stops_object_list[stop.number].expected_alight_pass += int(row[stop.name])

        # Calculate total pass in and input queue
        for stop in self.stops_object_list:
            stop.calculate_total_pass_in()

        globalConstants.results['Total_stops'] = len(self.stops_object_list)

    def generate_pass_input(self):
        start_time = time.time()

        if 0:
            # For each destination
            print("Setting empty pass lists")
            for i in range(len(self.stops_queue_list)):
                for j in range(len(self.stops_queue_list[i]['spl'])):
                    self.stops_queue_list[i]['spl'][j]['status'] = globalConstants.PASS_STATUS_EMPTY_255
                    self.stops_arrival_list[i]['spl'][j]['status'] = globalConstants.PASS_STATUS_EMPTY_255

            # Calculate total pass in and input queue
            for i in range(len(self.stops_object_list)):
                print("Generating pass input queue for stop name %s" % self.stops_object_list[i].name)
                # For each destination
                for key, val in enumerate(self.stops_object_list[i].destination_vector):
                    for j in range(val["dest_total"]):
                        k = self.stops_arrival_list[i]['last_empty']
                        self.stops_arrival_list[i]['spl'][k]['pass_id'] = globalConstants.pass_num
                        self.stops_arrival_list[i]['spl'][k]['orig_stop'] = int(self.stops_object_list[i].number)
                        self.stops_arrival_list[i]['spl'][k]['dest_stop'] = int(key)
                        self.stops_arrival_list[i]['spl'][k]['arrival_time'] = j*globalConstants.PASS_TOTAL_ARRIVAL_TIME/val["dest_total"]
                        self.stops_arrival_list[i]['spl'][k]['status'] = globalConstants.PASS_STATUS_TO_ARRIVE
                        self.stops_arrival_list[i]['total'] += 1
                        self.stops_arrival_list[i]['last_empty'] += 1
                        globalConstants.pass_num += 1

                # Sort items by arrival time ascending
                self.stops_arrival_list[i]['spl'].sort(order=['status', 'arrival_time'])
                if 0:
                    for p in self.stops_arrival_list[i]['spl']:
                        if p['status'] == globalConstants.PASS_STATUS_TO_ARRIVE:
                            print(p)
        else:
            # For each destination
            print("\nGenerating pass input queue all stops: %d" % len(self.stops_queue_list))
            for i in range(len(self.stops_queue_list)):
                masivo_c = ctypes.CDLL('./c_code/masivo_c.so')
                masivo_c.generate_pass.argtypes = (np.ctypeslib.ndpointer(dtype=globalConstants.spsl_type),
                                                   np.ctypeslib.ndpointer(dtype=globalConstants.spsl_type),
                                                   np.ctypeslib.ndpointer(dtype=globalConstants.dest_vec_type),
                                                   ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32)

                masivo_c.generate_pass(self.stops_queue_list,
                                       self.stops_arrival_list,
                                       self.stops_object_list[i].destination_vector,
                                       i,
                                       len(self.stops_object_list),
                                       len(self.stops_object_list[i].destination_vector))

                self.grand_total_passengers += int(self.stops_arrival_list[i]['total'])
                if 0:
                    for p in self.stops_arrival_list[i]['spl']:
                        if p['status'] == globalConstants.PASS_STATUS_TO_ARRIVE:
                            print(p)
        end_time = time.time()

        print("generate_pass_input_queue stops time %d ms, grand total passengers: %d"
              % ((end_time - start_time) * 1000, self.grand_total_passengers))
        globalConstants.results['Total_passengers'] = self.grand_total_passengers

    def prepare_cl(self):
        self.np_total_stops = np.uint32(len(self.stops_queue_list_g))
        self.total_work_items = self.np_total_stops + 10
        np_total_buses = np.uint32(len(self.buses_struc_list_g))
        self.knl.set_arg(0, self.stops_queue_list_g.data)
        self.knl.set_arg(1, self.stops_arrival_list_g.data)
        self.knl.set_arg(2, self.stops_alight_list_g.data)
        self.knl.set_arg(3, self.buses_struc_list_g.data)
        self.knl.set_arg(4, self.np_total_stops)
        self.knl.set_arg(5, np_total_buses)

    def runner_cl(self, sim_time):
        np_sim_time = np.uint32(sim_time)
        self.knl.set_arg(6, np_sim_time)
        evt = cl.enqueue_nd_range_kernel(self.queue, self.knl, (self.total_work_items,), None)
        evt.wait()

    def runner_c(self, sim_time):
        masivo_c = ctypes.CDLL('./c_code/masivo_c.so')
        masivo_c.masivo_runner.argtypes = (np.ctypeslib.ndpointer(dtype=globalConstants.spsl_type),
                                           np.ctypeslib.ndpointer(dtype=globalConstants.spsl_type),
                                           np.ctypeslib.ndpointer(dtype=globalConstants.spsl_type),
                                           np.ctypeslib.ndpointer(dtype=globalConstants.bpsl_type),
                                           ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32)

        masivo_c.masivo_runner(self.stops_queue_list,
                               self.stops_arrival_list,
                               self.stops_alight_list,
                               self.buses_struc_list,
                               len(self.stops_queue_list_g),
                               len(self.buses_struc_list),
                               sim_time)

    def runner(self, sim_time):

        # Update stop pass list from arrival list
        # For each stop
        for i in range(len(self.stops_queue_list)):

            # STOPS ARRIVAL:
            if self.stops_arrival_list[i]['total'] > 0:
                while True:
                    # Check if the list is finished
                    if self.stops_arrival_list[i]['w_index'] >= len(self.stops_arrival_list[i]['spl']):
                        break

                    # Check pass status
                    if self.stops_arrival_list[i]['spl'][self.stops_arrival_list[i]['w_index']]['status'] \
                            != globalConstants.PASS_STATUS_TO_ARRIVE:
                        break

                    # Check arrival time
                    if sim_time < self.stops_arrival_list[i]['spl'][self.stops_arrival_list[i]['w_index']][
                        'arrival_time']:
                        break

                    self.stops_queue_list[i]['spl'][self.stops_queue_list[i]['last_empty']] = \
                        np.copy(self.stops_arrival_list[i]['spl'][self.stops_arrival_list[i]['w_index']])
                    self.stops_queue_list[i]['spl'][self.stops_queue_list[i]['last_empty']][
                        'status'] = globalConstants.PASS_STATUS_ARRIVED
                    self.stops_queue_list[i]['last_empty'] += 1
                    self.stops_queue_list[i]['total'] += 1

                    self.stops_arrival_list[i]['spl'][self.stops_arrival_list[i]['w_index']]['status'] = \
                        globalConstants.PASS_STATUS_EMPTY

                    self.stops_arrival_list[i]['last_empty'] -= 1
                    self.stops_arrival_list[i]['total'] -= 1
                    self.stops_arrival_list[i]['w_index'] += 1

            # Handle the buses
            # For each bus
            for j in range(len(self.buses_struc_list)):
                # If the bus is in the stop
                if self.stops_queue_list[i]['stop_num'] == self.buses_struc_list[j]['curr_stop']:

                    if 1:
                        # ALIGHTING
                        # Only if there are passengers in the bus
                        if self.buses_struc_list[j]['total'] > 0:
                            # For each pass in the bus
                            for k in range(len(self.buses_struc_list[j]['bpl'])):
                                # print("pass to check(%d): %s " %(k, str(self.buses_struc_list[j]['bpl'][k])))
                                if self.buses_struc_list[j]['bpl'][k]['status'] == globalConstants.PASS_STATUS_IN_BUS:
                                    if self.buses_struc_list[j]['bpl'][k]['dest_stop'] == \
                                            self.stops_queue_list[i]['stop_num']:
                                        logging.info("ALIGHTING pass %s from bus %d to stop %d" %
                                                     (str(self.buses_struc_list[j]['bpl'][k]), j,
                                                      self.stops_queue_list[i]['stop_num']))

                                        self.buses_struc_list[j]['bpl'][k][
                                            'status'] = globalConstants.PASS_STATUS_ALIGHTED
                                        self.buses_struc_list[j]['bpl'][k]['alight_time'] = sim_time
                                        self.buses_struc_list[j]['total'] -= 1
                                        self.buses_struc_list[j]['last_empty'] -= 1

                                        m = self.stops_alight_list[i]['last_empty']
                                        self.stops_alight_list[i]['spl'][m] = np.copy(
                                            self.buses_struc_list[j]['bpl'][k])
                                        self.stops_alight_list[i]['total'] += 1
                                        self.stops_alight_list[i]['last_empty'] += 1

                    # BOARDING
                    # If there are pass in the stop, do not look for more buses
                    if self.stops_queue_list[i]['total'] == 0:
                        break

                    # If the bus is full, continue with the next bus
                    if self.buses_struc_list[j]['total'] >= globalConstants.BUS_MAX_PASS:
                        continue

                    # For this bus, begin the free space search from the beginning
                    self.buses_struc_list[j]['last_empty'] = 0

                    # For each pass in the stop
                    for k in range(len(self.stops_queue_list[i]['spl'])):

                        # print("Check for board: %s" % (self.pass_list[i]['spl'][k]))
                        # If the bus is full, continue with the next bus
                        if self.buses_struc_list[j]['total'] >= globalConstants.BUS_MAX_PASS:
                            break

                        # If we are at the end of the pass list
                        if self.stops_queue_list[i]['spl'][k]['status'] == globalConstants.PASS_STATUS_EMPTY_255:
                            break

                        # If the pass has arrived to the stop
                        if self.stops_queue_list[i]['spl'][k]['status'] == globalConstants.PASS_STATUS_ARRIVED:

                            # Check if the bus route has the pass destination stop
                            bus_for_dest = False
                            # print("Bus %d in stop %d, last stop i %d" %
                            # (j, i, self.buses_struc_list[j]['last_stop_i']))
                            for l in (range(self.buses_struc_list[j]['last_stop_table_i'],
                                            self.buses_struc_list[j]['total_stops'])):
                                if self.stops_queue_list[i]['spl'][k]['dest_stop'] == \
                                        self.buses_struc_list[j]['stops_num'][l]:
                                    bus_for_dest = True
                                    break

                            # If the bus has the destination stop, pass boards
                            if bus_for_dest:
                                # Look for a free space in the bus
                                for n in range(self.buses_struc_list[j]['last_empty'],
                                               len(self.buses_struc_list[j]['bpl'])):
                                    # print("bus seat: %d, %s" % (n, str(self.buses_struc_list[j]['bpl'][n])))

                                    if self.buses_struc_list[j]['bpl'][n]['status'] == \
                                            globalConstants.PASS_STATUS_IN_BUS:
                                        # print("busy")
                                        continue

                                    logging.info("BOARDING pass %s to the bus %d, in poss %d" %
                                                 (str(self.stops_queue_list[i]['spl'][k]), j, n))

                                    self.stops_queue_list[i]['spl'][k]['status'] = globalConstants.PASS_STATUS_IN_BUS
                                    self.stops_queue_list[i]['total'] -= 1

                                    self.buses_struc_list[j]['bpl'][n] = np.copy(self.stops_queue_list[i]['spl'][k])
                                    self.buses_struc_list[j]['total'] += 1
                                    self.buses_struc_list[j]['last_empty'] = n
                                    break

                            # If bus is full break to go to the next bus in the stop
                            if self.buses_struc_list[j]['total'] >= globalConstants.BUS_MAX_PASS:
                                break

        # Update buses
        if 1:
            # For each bus
            for i in range(len(self.buses_struc_list)):
                # Do not process finished buses
                if self.buses_struc_list[i]['curr_stop'] == globalConstants.BUS_FINISHED:
                    continue

                # Check if start the bus
                if self.buses_struc_list[i]['curr_stop'] == globalConstants.BUS_NOT_STARTED_STOP:
                    if sim_time >= self.buses_struc_list[i]['start_time']:
                        self.buses_struc_list[i]['in_the_stop'] = True
                        self.buses_struc_list[i]['curr_stop'] = self.buses_struc_list[i]['stops_num'][0]
                        self.buses_struc_list[i]["last_stop_i"] = self.buses_struc_list[i]['stops_num'][0]
                        self.buses_struc_list[i]["curr_pos"] = self.buses_struc_list[i]["start_pos"]
                        self.buses_struc_list[i]['last_stop_pos'] = self.buses_struc_list[i]["curr_pos"]

                        logging.info("Starting bus %d in stop %d start time %d",
                                     self.buses_struc_list[i]["number"],
                                     self.buses_struc_list[i]['curr_stop'],
                                     self.buses_struc_list[i]['start_time'])
                        # self.bl_head += 1
                    continue

                # self.buses_struc_list[i].update_pos(self.stops_list)

                # Update bus possition

                # If waiting in the stop
                # print("Bus: %d, in_the_stop_flag: %d, curr_stop %d, pos: %d" %
                #      (self.buses_struc_list[i]['number'],
                #       self.buses_struc_list[i]["in_the_stop"],
                #       self.buses_struc_list[i]['curr_stop'],
                #       self.buses_struc_list[i]['curr_pos']))

                # Check if we have to depart from the stop
                if self.buses_struc_list[i]["in_the_stop"]:
                    self.buses_struc_list[i]["in_the_stop_counter"] -= 1
                    if self.buses_struc_list[i]["in_the_stop_counter"] == 0:
                        self.buses_struc_list[i]["last_stop_table_i"] += 1
                        self.buses_struc_list[i]["in_the_stop"] = False
                        self.buses_struc_list[i]["curr_stop"] = globalConstants.BUS_TRAVELING

                # If I am not waiting in a stop, go ahead
                if self.buses_struc_list[i]["curr_stop"] == globalConstants.BUS_TRAVELING:
                    self.buses_struc_list[i]["curr_pos"] += self.buses_struc_list[i]["travel_speed_m_s"]

                # Check if the bus has to leave the current stop, if not, do not check for other stop
                if abs(self.buses_struc_list[i]['last_stop_pos'] - self.buses_struc_list[i]["curr_pos"]) < \
                        globalConstants.STOP_BUS_WINDOW_DISTANCE:
                    continue

                # Check if the bus is at the next stop
                next_stop_i = self.buses_struc_list[i]["last_stop_i"] + self.buses_struc_list[i]['stop_inc']
                # print("next_stop_i: %d/%d" % (next_stop_i, self.buses_struc_list[i]['total_stops']))

                # Check if the next stop is the last one
                if next_stop_i >= self.buses_struc_list[i]['total_stops'] or next_stop_i < 0:
                    # Finish the bus and put in the rest position
                    self.buses_struc_list[i]["curr_stop"] = globalConstants.BUS_FINISHED
                    self.buses_struc_list[i]["curr_pos"] = 0
                    continue

                # Look if the bus is inside the stop window of the next stop
                if abs(self.stops_queue_list[next_stop_i]['stop_pos'] - self.buses_struc_list[i]["curr_pos"]) \
                        < globalConstants.STOP_BUS_WINDOW_DISTANCE:

                    # Passing the stop, update last stop index
                    self.buses_struc_list[i]["last_stop_i"] = self.stops_queue_list[next_stop_i]['stop_num']

                    # Check if the stop is in the routes table to stop de bus
                    in_the_route = False
                    for j in range(self.buses_struc_list[i]["stops_num_i"], self.buses_struc_list[i]["total_stops"]):
                        if self.stops_queue_list[next_stop_i]['stop_num'] == self.buses_struc_list[i]["stops_num"][j]:
                            self.buses_struc_list[i]["stops_num_i"] = j
                            in_the_route = True

                    # If this stop is in the stops table
                    if in_the_route:
                        logging.info("i: %d, Bus %d, in the stop: %d, pos %d" % (i,
                                                                                 self.buses_struc_list[i]['number'],
                                                                                 self.stops_queue_list[next_stop_i][
                                                                                     'stop_num'],
                                                                                 self.buses_struc_list[i]['curr_pos']))
                        self.buses_struc_list[i]['curr_stop'] = self.stops_queue_list[next_stop_i]['stop_num']
                        self.buses_struc_list[i]['last_stop_pos'] = self.stops_queue_list[next_stop_i]['stop_pos']
                        self.buses_struc_list[i]['in_the_stop'] = True
                        self.buses_struc_list[i]['in_the_stop_counter'] = globalConstants.BUS_STOPPING_TIME
