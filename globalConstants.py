import logging
import numpy as np

# Global variables
pass_num = 0
stops_name_to_num = {}

# Graph configuration constants
BUS_AND_STOPS_SCALE = 20
PASS_TOTAL_ARRIVAL_TIME = 50     # In secs
LOGGING_LEVEL = logging.INFO

test_scenario = 3
cl_enabled = False

if test_scenario == 3:
  ODM_FILE = 'utils/odm3small.csv'
  ROUTES_FILE = 'utils/routes3small.csv'
if test_scenario == 30:
  ODM_FILE = 'utils/odm30.csv'
  ROUTES_FILE = 'utils/routes30.csv'
if test_scenario == 300:
  ODM_FILE = 'utils/odm300.csv'
  ROUTES_FILE = 'utils/routes300.csv'

STOP_MAX_PASS = 10000
BUS_MAX_PASS = 200
TOTAL_BUSES = 100
STOP_BUS_WINDOW_DISTANCE = 10
MAX_STOPS = 500

BUS_NOT_STARTED_STOP = 20000
BUS_TRAVELING = 20001
EMPTY_STOP_NUMBER = 20000

# Masivo fixed constants, DO NOT MODIFY !!!!
PASS_TYPE = np.dtype([('pass_id', 'u4'), ('orig_stop', 'u2'), ('dest_stop', 'u2'),
                      ('arrival_time', 'u2'), ('alight_time', 'u2'), ('status', 'u1')])

# Stop Passengers List (SPL)
spl_type = np.dtype((PASS_TYPE, STOP_MAX_PASS))
# Stop Passengers Struct List (SPSL)
spsl_type = np.dtype([('stop_num', 'u2'), ('total', 'u4'), ('last_empty', 'u4'), ('w_index', 'u4'), ('spl', spl_type)])

# Bus Passengers List (BPL)
bpl_type = np.dtype((PASS_TYPE, BUS_MAX_PASS))
# Bus Passengers Struct List (BPSL)
bpsl_type = np.dtype([('curr_stop', 'u2'), ('last_stop_i', 'u2'), ('stops_num', 'u2', MAX_STOPS),
                      ('total', 'u4'), ('last_empty', 'u4'), ('w_index', 'u4'), ('bpl', bpl_type)])


PASS_STATUS_EMPTY_255 = 255
PASS_STATUS_EMPTY = 0
PASS_STATUS_TO_ARRIVE = 1
PASS_STATUS_ARRIVED = 2
PASS_STATUS_IN_BUS = 3
PASS_STATUS_ALIGHTED = 4



