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
BUS_AVG_SPEED = 54*1000/3600
BUS_STOPPING_TIME = 20
TOTAL_BUSES = 100
STOP_BUS_WINDOW_DISTANCE = 20
MAX_STOPS = 500
PERFORMANCE_ODR = 100

test_scenario = 30

LIMIT_MAX_CPUS = 0              # 0 unlimited

PANDA_3D_ENABLED = 0
SIM_ACCEL_RATE = 0            # 0 unlimited

USE_PYTHON = 1
USE_PYOPENCL = 0
USE_PYTHON_C = 0


if test_scenario == 3:
    END_SIM_TIME = 3600 * 2
    if 0:
        ODM_FILE = '../../inputs/odm3.csv'
        ROUTES_FILE = '../../inputs/routes3.csv'
    else:
        ODM_FILE = '../../inputs/odm3small.csv'
        ROUTES_FILE = '../../inputs/routes3small.csv'
if test_scenario == 30:
    END_SIM_TIME = 3600 * 2
    ODM_FILE = '../../inputs/odm30_random.csv'
    ROUTES_FILE = '../../inputs/routes30.csv'
if test_scenario == 300:
    END_SIM_TIME = 3600 * 10
    ODM_FILE = '../../inputs/odm300.csv'
    ROUTES_FILE = '../../inputs/routes300.csv'

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
PASS_DATA_FORMAT = 'HHHHL'     # (alight_time, arrival_time, dest_stop, orig_stop, pass_id)
PASS_TYPE = np.dtype([('pass_id', 'u4'), ('orig_stop', 'u2'), ('dest_stop', 'u2'),
                      ('arrival_time', 'u2'), ('alight_time', 'u2'), ('status', 'u1')])
STOP_BUS_WINDOW_DISTANCE = 10


STOP_MAX_PASS = 8000

PASS_STATUS_EMPTY_255 = 255
PASS_STATUS_EMPTY = 0
PASS_STATUS_TO_ARRIVE = 1
PASS_STATUS_ARRIVED = 2
PASS_STATUS_IN_BUS = 3
PASS_STATUS_ALIGHTED = 4

STATUS_TEXT_ARRAY = ['EMPTY', 'TO ARRIVE', 'ARRIVED', 'IN BUS', 'ALIGHTED']

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
    'LIMIT_MAX_CPUS': 0,
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
