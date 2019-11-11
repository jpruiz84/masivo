from Stop import Stop
import sys
import time
import logging
import globalConstants
from BusesHandler import BusesHandler
from StopsHandler import StopsHandler
from graphs2d.Graphs2d import Graphs2d
import os
import results
import psutil

class Masivo:
    def __init__(self):

        # Configuring logging format
        # logging.basicConfig(format='%(asctime)s %(message)s', level=globalConstants.LOGGING_LEVEL)
        logging.basicConfig(format='%(message)s', level=globalConstants.LOGGING_LEVEL)
        print("\n\n|||||||||| Starting Masivo public transport simulator ||||||||||\n")

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
        self.stops_list = self.stops_handler.get_stops_list()
        self.stops_pass_list = self.stops_handler.get_stops_list()
        self.stops_handler.get_stops_alight_list()
        self.cl_queue = self.stops_handler.get_cl_queue()

        # Init buses
        self.buses_handler = BusesHandler(self.stops_list, self.cl_queue)
        self.buses_list = self.buses_handler.get_buses_list()
        self.buses_struc_list = self.buses_handler.get_bus_struc_list()
        self.buses_struc_list_g = self.buses_handler.get_bus_struc_list_g()

        # Set the buses_struct_list in the stops handler
        self.stops_handler.set_buses_struc_list(self.buses_struc_list)
        self.stops_handler.set_buses_struc_list_g(self.buses_struc_list_g)
        self.stops_handler.set_buses_handler(self.buses_handler)

        # Set masivo_data for panda3d
        self.masivo_data["stops_list"] = self.stops_list
        self.masivo_data["buses_list"] = self.buses_list

        # Create output folders if not exist
        if not os.path.exists(os.path.join(globalConstants.RESULTS_FOLDER_NAME)):
            os.makedirs(os.path.join(globalConstants.RESULTS_FOLDER_NAME))



    # Main run
    def run(self):
        total_start_time = time.time()

        if globalConstants.USE_PYOPENCL:
            self.stops_handler.prepare_cl()

        start_perf_time = time.time()
        for sim_time in range(0, globalConstants.END_SIM_TIME):
            start_op_time = time.time()

            if globalConstants.USE_PYOPENCL:
                self.stops_handler.runner_cl(sim_time)
            if globalConstants.USE_PYTHON_C:
                self.stops_handler.runner_c(sim_time)
            if globalConstants.USE_PYTHON:
                self.stops_handler.runner(sim_time)

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
        print("\nTotal execution time: %.3f s" % (total_end_time - total_start_time))
        globalConstants.results['Total_execution_time'] = \
            '{:0.3f}'.format(total_end_time - total_start_time)
        print("")

        if 0:
            print('\nBuses list:')
            for i in range(len(self.buses_handler.get_final_bus_struc_list())):
                if self.buses_handler.get_final_bus_struc_list()[i]['total'] > 0:
                    print("Bus %s , route %s \t has %d pass, \t final pos %d" %
                          (self.buses_list[i].number, self.buses_list[i].route.name,
                           self.buses_handler.get_final_bus_struc_list()[i]['total'],
                           self.buses_handler.get_final_bus_struc_list()[i]['curr_pos']))

        self.graphs2d.served_passengers(self.masivo_data["stops_list"])
        self.graphs2d.performance_graph(self.performance, self.masivo_data["stops_list"])
        self.graphs2d.save_performance_csv(self.performance)
        #self.graphs2d.commute_time(self.stops_handler.get_stops_alight_list())

        #results.passengers_results(self.stops_handler, self.buses_handler)
        results.simulation_brief(globalConstants.results)

        if globalConstants.USE_PYTHON:
            print("Python Total time: %f s" % (total_end_time - total_start_time))
        elif globalConstants.USE_PYOPENCL:
            print("PyCL Total time: %f s" % (total_end_time - total_start_time))
        elif globalConstants.USE_PYTHON_C:
            print("PyC Total time: %f s" % (total_end_time - total_start_time))
        else:
            print("Total time: %f s" % (total_end_time - total_start_time))

    def get_masivo_data(self):
        return self.masivo_data
