import globalConstants
import numpy as np
import logging
import copy


class Bus:

    def __init__(self, number, route, stops_list):
        self.number = number
        self.route = route
        self.max_capacity = globalConstants.BUS_MAX_PASS
        self.pass_queue = []
        self.travel_speed_m_s = globalConstants.BUS_AVG_SPEED
        self.start_time = 0
        self.bus_struc = 0
        self.bus_struc_g = 0
        self.stop_inc = 1
        self.total_stops = len(stops_list)
        self.stop_index = 0

        if route.dir == 'W-E':
            self.y_pos = 950
            self.stop_inc = 1
            self.last_stop_index = 0
        else:
            self.y_pos = 1050
            self.travel_speed_m_s *= -1
            self.stop_inc = -1
            self.last_stop_index = self.total_stops - 1

    def set_list(self, bus_struc):
        self.bus_struc = bus_struc
        self.bus_struc['total_stops'] = self.total_stops
        self.bus_struc['start_time'] = self.start_time
        self.bus_struc['stop_inc'] = self.stop_inc
        self.bus_struc['number'] = self.number
        self.bus_struc['travel_speed_m_s'] = self.travel_speed_m_s
        self.bus_struc['curr_stop'] = self.bus_struc['stops_num'][0]
        self.bus_struc['in_the_stop_counter'] = globalConstants.BUS_STOPPING_TIME
        self.bus_struc["start_pos"] = self.route.start_stop.x_pos
        self.bus_struc["curr_pos"] = 0
        self.bus_struc['last_stop_pos'] = self.bus_struc["curr_pos"]
        self.bus_struc["last_stop_i"] = self.bus_struc['stops_num'][0]

    def set_cl_list(self, bus_struc_g):
        self.bus_struc_g = bus_struc_g

    def pass_in(self, pass_id):
        if len(self.pass_queue) < self.max_capacity:
            self.pass_queue.append(pass_id)
            return True
        else:
            return False

    def pass_out(self):
        if len(self.pass_queue):
            return self.pass_queue.pop(0)
        else:
            return ""

    def pass_count(self):
        if globalConstants.cl_enabled:
            return np.array(self.bus_struc_g.get(), dtype=globalConstants.bpsl_type)['total']
        else:
            return self.bus_struc['total']

    def get_x_pos(self):
        if globalConstants.cl_enabled:
            return np.array(self.bus_struc_g.get(), dtype=globalConstants.bpsl_type)['curr_pos']
        else:
            return self.self.bus_struc["curr_pos"]


    def get_number(self):
        return self.number

    def is_full(self):
        if self.pass_count() >= self.max_capacity:
            return True
        else:
            return False

    def is_finished(self):
        if self.bus_struc["curr_stop"] == globalConstants.BUS_FINISHED:
            logging.info("Bus %d is finished" % self.number)
            return True
        return False

    def update_pos(self, stops_list):
        # If waiting in the stop
        # print("Bus: %d, in the stop: %d, curr_stop %d" % (self.number, self.bus_struc["in_the_stop"], self.bus_struc['curr_stop']))
        if self.bus_struc["in_the_stop"]:

            # Check if we have to depart from the stop
            self.bus_struc["in_the_stop_counter"] -= 1
            if self.bus_struc["in_the_stop_counter"] == 0:
                self.bus_struc["last_stop_table_i"] += 1
                self.bus_struc["in_the_stop"] = False
                self.bus_struc["curr_stop"] = globalConstants.BUS_TRAVELING

        # If I am not waiting in a stop, go ahead
        if self.bus_struc["curr_stop"] == globalConstants.BUS_TRAVELING:
            self.bus_struc["curr_pos"] += self.travel_speed_m_s

        # Check if the bus has to leave the current stop, if not, do not check for other stop
        if abs(self.bus_struc['last_stop_pos'] - self.bus_struc["curr_pos"]) < globalConstants.STOP_BUS_WINDOW_DISTANCE:
            return

        # Check if the bus is at the next stop
        next_stop_i = self.bus_struc["last_stop_i"] + self.bus_struc['stop_inc']
        # print("next_stop_i: %d/%d" % (next_stop_i, self.bus_struc['total_stops']))

        # Check if the next stop is the last one
        if next_stop_i >= self.bus_struc['total_stops'] or next_stop_i < 0:
            # Finish the bus and put in the rest position
            self.bus_struc["curr_stop"] = globalConstants.BUS_FINISHED
            self.bus_struc["curr_pos"] = 0
            return

        # Look if the bus is inside the stop window of the next stop
        if abs(stops_list[next_stop_i].position - self.bus_struc["curr_pos"]) \
                < globalConstants.STOP_BUS_WINDOW_DISTANCE:

            # Passing the stop, update last stop index
            self.bus_struc["last_stop_i"] = stops_list[next_stop_i].number

            # Check if the stop is in the routes table to stop de bus
            in_the_route = False
            for i in range(self.bus_struc["stops_num_i"], self.bus_struc["total_stops"]):
                if stops_list[next_stop_i].number == self.bus_struc["stops_num"][i]:
                    self.bus_struc["stops_num_i"] = i
                    in_the_route = True

            # If this stop is in the stops table
            if in_the_route:
                logging.info("Bus %s, in the stop: %s, pos %d, is full: %s" % (
                    self.number, stops_list[next_stop_i].name, self.bus_struc['curr_pos'], str(self.is_full())))
                self.bus_struc['curr_stop'] = stops_list[next_stop_i].number
                self.bus_struc['last_stop_pos'] = stops_list[next_stop_i].position
                self.bus_struc['in_the_stop'] = True
                self.bus_struc['in_the_stop_counter'] = globalConstants.BUS_STOPPING_TIME
