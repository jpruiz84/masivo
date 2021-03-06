from Stop import Stop
import sys
import time
import logging
import globalConstants
from BusesHandler import BusesHandler
from StopsHandler import StopsHandler
from graphs2d.Graphs2d import Graphs2d
from struct import *
import results
import psutil
import os

class Masivo:
    def __init__(self):

        # Configuring logging format
        # logging.basicConfig(format='%(asctime)s %(message)s', level=globalConstants.LOGGING_LEVEL)
        logging.basicConfig(format='%(message)s', level=globalConstants.LOGGING_LEVEL)
        print("\n\n|||||||||| Starting Masivo (Pure Python) public transport simulator ||||||||||\n")

        # Init objects
        self.graphs2d = Graphs2d()

        # Init variables and lists
        self.pass_id_num = 0
        self.masivo_data = {}
        self.stops_list = []
        self.buses_list = []
        self.finished_buses_list = []
        self.performance = {"time": [], "rtf": [], "cpu_usage": [], "cpu_freq": []}

        # Init stops
        self.stops_handler = StopsHandler()
        self.stops_list = self.stops_handler.get_stop_list()

        # Init buses
        self.buses_handler = BusesHandler(self.stops_list)
        self.buses_list = self.buses_handler.get_buses_list()
        self.finished_buses_list = self.buses_handler.get_finished_buses_list()

        self.masivo_data["stops_list"] = self.stops_list
        self.masivo_data["buses_list"] = self.buses_list

        # Create output folders if not exist
        if not os.path.exists(os.path.join(globalConstants.RESULTS_FOLDER_NAME)):
            os.makedirs(os.path.join(globalConstants.RESULTS_FOLDER_NAME))


    # Main run
    def run(self):
        total_start_time = time.time()

        start_perf_time = time.time()
        for sim_time in range(0, globalConstants.END_SIM_TIME):
            start_op_time = time.time()

            self.stops_handler.runner(sim_time)
            self.buses_handler.runner(sim_time)

            if (sim_time % globalConstants.PERFORMANCE_ODR) == 0:
                if(sim_time / globalConstants.PERFORMANCE_ODR) > 2:
                    self.performance["time"].append(sim_time)
                    self.performance["rtf"].append(
                        globalConstants.PERFORMANCE_ODR / (time.time() - start_perf_time))
                    self.performance["cpu_usage"].append(psutil.cpu_percent())
                    self.performance["cpu_freq"].append(psutil.cpu_freq().current)

                start_perf_time = time.time()
                sys.stdout.write("\rtime: %d  " % sim_time)
                sys.stdout.flush()

            if globalConstants.SIM_ACCEL_RATE > 0:
                rem_time = (1 / globalConstants.SIM_ACCEL_RATE) - (time.time() - start_op_time)
                time.sleep(rem_time)

        total_end_time = time.time()

        # END SIMULATION, log results
        print("\nEND SIMULATION !!!!!")
        print("Total present buses: %d" % len(self.buses_list))
        print("Total finished buses: %d" % len(self.finished_buses_list))
        print("Total stops: %d" % len(self.masivo_data["stops_list"]))
        print("\nTotal execution time: %f s" % (total_end_time - total_start_time))
        globalConstants.results['Total_execution_time'] = \
            '{:0.3f}'.format(total_end_time - total_start_time)
        print("")

        for stop in self.masivo_data["stops_list"]:
            print("Stop %s have %d/%d pass, and %d/%d out" % (stop.name, stop.pass_count(), len(stop.pass_arrival_list),
                                                              stop.pass_alight_count(), stop.expected_alight_pass))
        print("")

        if 0:
          for bus in self.finished_buses_list:
              print("Present Bus %s have %d pass, final poss %d" % (
              bus.get_number(), bus.pass_count(), bus.current_position))

          for bus in self.finished_buses_list:
              print("Finished bus %s have %d pass, final poss %d" % (
              bus.get_number(), bus.pass_count(), bus.current_position))

        self.graphs2d.served_passengers(self.masivo_data["stops_list"])
        self.graphs2d.performance_graph(self.performance, total_end_time - total_start_time)
        self.graphs2d.commute_time(self.stops_list)

        if 0:
            for stop in self.stops_list:
                for pass_pack in stop.pass_alight_list:
                    (alight_time, arrival_time, dest_stop, orig_stop, pass_id) = \
                        unpack(globalConstants.PASS_DATA_FORMAT, pass_pack)
                    print("pass_id %d \torig_stop %d \tdest_stop %d \tarrival_time %d \t alight_time %d" %
                          (pass_id, orig_stop, dest_stop, arrival_time, alight_time))



        results.passengers_results(self.stops_list, self.buses_list)
        results.simulation_brief(globalConstants.results)

        print("\nTotal execution time: %f s" % (total_end_time - total_start_time))


    def get_masivo_data(self):
        return self.masivo_data
