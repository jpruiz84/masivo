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
BUS_STOPPING_TIME = 20
TOTAL_BUSES = 100
STOP_BUS_WINDOW_DISTANCE = 10
MAX_STOPS = 500
PERFORMANCE_ODR = 30

test_scenario = 3

PANDA_3D_ENABLED = False
SIM_ACCEL_RATE = 0
END_SIM_TIME = 3600*2

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
    ODM_FILE = 'inputs/odm30.csv'
    ROUTES_FILE = 'inputs/routes30.csv'
if test_scenario == 300:
    ODM_FILE = 'inputs/odm300.csv'
    ROUTES_FILE = 'inputs/routes300.csv'

BUS_NOT_STARTED_STOP = 20000
BUS_TRAVELING = 20001
BUS_FINISHED = 20002
EMPTY_STOP_NUMBER = 20000

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
                      ('last_empty', 'u4'),
                      ('w_index', 'u4'),
                      ('bpl', bpl_type)])

dest_vec_type = np.dtype([('dest_total', 'u4')])


PASS_STATUS_EMPTY_255 = 255
PASS_STATUS_EMPTY = 0
PASS_STATUS_TO_ARRIVE = 1
PASS_STATUS_ARRIVED = 2
PASS_STATUS_IN_BUS = 3
PASS_STATUS_ALIGHTED = 4

RESULTS_FOLDER = 'results'

if USE_PYOPENCL:
    cl_enabled = True
else:
    cl_enabled = False