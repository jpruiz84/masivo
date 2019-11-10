import logging
import numpy as np

# Global variables
pass_num = 0
stops_name_to_num = {}

# Graph configuration constants
BUS_AND_STOPS_SCALE = 20

# Masivo configuration
PASS_TOTAL_ARRIVAL_TIME = 3600  # In secs
LOGGING_LEVEL = logging.ERROR
STOP_MAX_PASS = 10000
BUS_MAX_PASS = 250
BUS_AVG_SPEED = 54 * 1000 / 3600
BUS_STOPPING_TIME = 20
STOP_BUS_WINDOW_DISTANCE = 20
MAX_STOPS = 500
PERFORMANCE_ODR = 100

test_scenario = 3

LIMIT_MAX_CPUS = 0  # 0 unlimited

PANDA_3D_ENABLED = False
SIM_ACCEL_RATE = 0  # 0 unlimited
END_SIM_TIME = 3600 * 2

USE_PYTHON = 0
USE_PYOPENCL = 1
USE_PYTHON_C = 0

if test_scenario == 3:
    if 1:
        ODM_FILE = 'inputs/odm3.csv'
        ROUTES_FILE = 'inputs/routes3.csv'
    else:
        ODM_FILE = 'inputs/odm3small.csv'
        ROUTES_FILE = 'inputs/routes3small.csv'
if test_scenario == 30:
    ODM_FILE = 'inputs/odm30_random.csv'
    ROUTES_FILE = 'inputs/routes30.csv'
if test_scenario == 300:
    ODM_FILE = 'inputs/odm300.csv'
    ROUTES_FILE = 'inputs/routes300.csv'

BUS_NOT_STARTED_STOP = 20000
BUS_TRAVELING = 20001
BUS_FINISHED = 20002
EMPTY_STOP_NUMBER = 20000

# Output file names
RESULTS_FOLDER_NAME = 'results'

# Passengers served information output files
PASSENGERS_ALIGHTED_FILE_NAME = 'total_passengers_results.csv'
PASSENGERS_ALIGHTED_PER_STOP_FILE_NAME = 'served_passengers_per_stop.csv'
GRAPH_SERVED_PASSENGERS_FILE_NAME = 'served_passengers_per_stop.eps'
GRAPH_COMMUTE_TIME_PER_STOP_FILE_NAME = 'commute_time_per_stop.eps'

# Performance output files
GRAPH_PERFORMANCE_TIMELINE_FILE_NAME = 'performance_timeline.eps'
CSV_PERFORMANCE_TIMELINE_FILE_NAME = 'performance_timeline.csv'

SIMULATION_BRIEF_FILE_NAME = 'simulation_brief.csv'

# Masivo fixed constants, DO NOT MODIFY !!!!
PASS_TYPE = np.dtype([('pass_id', 'u4'),
                      ('orig_stop', 'u2'),
                      ('dest_stop', 'u2'),
                      ('arrival_time', 'u2'),
                      ('alight_time', 'u2'),
                      ('status', 'u1')])

# Stop Passengers List (SPL)
spl_type = np.dtype((PASS_TYPE, STOP_MAX_PASS))
# Stop Passengers Struct List (SPSL)
spsl_type = np.dtype([('stop_num', 'u2'),
                      ('stop_pos', 'i4'),
                      ('total', 'u4'),
                      ('last_empty', 'u4'),
                      ('w_index', 'u4'),
                      ('spl', spl_type)])

# Bus Passengers List (BPL)
bpl_type = np.dtype((PASS_TYPE, BUS_MAX_PASS))
# Bus Passengers Structure List (BPSL)
bpsl_type = np.dtype([('number', 'u2'),
                      ('travel_speed_m_s', 'i2'),
                      ('start_pos', 'i4'),
                      ('last_stop_table_i', 'u2'),
                      ('last_stop_pos', 'i4'),
                      ('start_time', 'u4'),
                      ('stops_num_i', 'u2'),
                      ('stop_inc', 'i2'),
                      ('in_the_stop_counter', 'u2'),
                      ('in_the_stop', 'u2'),
                      ('curr_pos', 'i4'),
                      ('curr_stop', 'u2'),
                      ('last_stop_i', 'u2'),
                      ('total_stops', 'u2'),
                      ('stops_num', 'u2', MAX_STOPS),
                      ('total', 'u4'),
                      ('bpl', bpl_type)])

dest_vec_type = np.dtype([('dest_total', 'u4')])

PASS_STATUS_EMPTY_255 = 255
PASS_STATUS_EMPTY = 0
PASS_STATUS_TO_ARRIVE = 1
PASS_STATUS_ARRIVED = 2
PASS_STATUS_IN_BUS = 3
PASS_STATUS_ALIGHTED = 4

STATUS_TEXT_ARRAY = ['EMPTY', 'TO ARRIVE', 'ARRIVED', 'IN BUS', 'ALIGHTED']

if USE_PYOPENCL:
    cl_enabled = True
else:
    cl_enabled = False

results = {
    'PASS_TOTAL_ARRIVAL_TIME': PASS_TOTAL_ARRIVAL_TIME,
    'STOP_MAX_PASS': STOP_MAX_PASS,
    'BUS_MAX_PASS': BUS_MAX_PASS,
    'BUS_AVG_SPEED': BUS_AVG_SPEED,
    'BUS_STOPPING_TIME': BUS_STOPPING_TIME,
    'STOP_BUS_WINDOW_DISTANCE': STOP_BUS_WINDOW_DISTANCE,
    'MAX_STOPS': MAX_STOPS,
    'PERFORMANCE_ODR': PERFORMANCE_ODR,
    'test_scenario': test_scenario,
    'LIMIT_MAX_CPUS': LIMIT_MAX_CPUS,
    'PANDA_3D_ENABLED': PANDA_3D_ENABLED,
    'SIM_ACCEL_RATE': SIM_ACCEL_RATE,
    'END_SIM_TIME': END_SIM_TIME,
    'USE_PYTHON': USE_PYTHON,
    'USE_PYOPENCL': USE_PYOPENCL,
    'USE_PYTHON_C': USE_PYTHON_C,
    'ODM_FILE': ODM_FILE,
    'ROUTES_FILE': ROUTES_FILE,
    'Total_stops': 0,
    'Total_routes': 0,
    'Total_buses': 0,
    'Total_passengers': 0,
    'Total_alighted_passengers': 0,
    'Total_alighted_expected_passengers': 0,
    'Total_average_commute_time': 0,
    'Total_execution_time': 0,
    'Average_real_time_factor': 0,
    'Average_cpu_usage': 0,
    'OpenCL_device_name': '',
}  # To storage the simulation results brief

# Default colors and markers for the graphs
COLORS_TAB10 = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
