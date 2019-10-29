import globalConstants
import random
from struct import *
import logging
import numpy as np
from sys import getsizeof


class Stop:

    def __init__(self, number, name, x_pos, y_pos, max_capacity):
        self.number = number
        self.name = name
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.position = x_pos  # TODO: delete later, for legacy compatibility 1D
        self.max_capacity = max_capacity
        self.total_pass_in = 0
        self.pass_id_num = 0

        self.pass_list = 0
        self.pass_arrival_list = 0
        self.pass_alight_list = 0

        self.pass_list_g = 0
        self.pass_arrival_list_g = 0
        self.pass_alight_list_g = 0

        self.destination_vector = 0
        self.expected_alight_pass = 0
        self.last_arrived_index = 0
        self.sap_index = 0

    def set_stop_lists(self, pass_list, pass_arrival_list, pass_alight_list):
        self.pass_list = pass_list
        self.pass_arrival_list = pass_arrival_list
        self.pass_alight_list = pass_alight_list
        self.pass_list['stop_pos'] = self.x_pos

    def set_cl_lists(self, pass_list, pass_arrival_list, pass_alight_list):
        self.pass_list_g = pass_list
        self.pass_arrival_list_g = pass_arrival_list
        self.pass_alight_list_g = pass_alight_list

    def pass_count(self):
        if globalConstants.cl_enabled:
            return np.array(self.pass_list_g.get(), dtype=globalConstants.spsl_type)['total']
        else:
            return self.pass_list['total']

    def pass_alight_count(self):
        if globalConstants.cl_enabled:
            return np.array(self.pass_alight_list_g.get(), dtype=globalConstants.spsl_type)['total']
        else:
            return self.pass_alight_list['total']

    def calculate_total_pass_in(self):
        self.total_pass_in = 0
        for d in self.destination_vector:
            self.total_pass_in += d['dest_total']

    @staticmethod
    def get_pass_arrival_time(pass_pack):
        (alight_time, arrival_time, dest_stop, orig_stop, pass_id) = \
            unpack(globalConstants.PASS_DATA_FORMAT, pass_pack)
        return arrival_time

    def runner(self, sim_time):
        # Pass arrives to the stop
        if len(self.pass_arrival_list) > 0:
            while sim_time == self.pass_arrival_list[0]['arrival_time']:
                self.pass_in(self.pass_arrival_list.pop(0))
                if len(self.pass_arrival_list) == 0:
                    break
