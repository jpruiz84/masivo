import logging
import numpy as np

# Global variables
pass_num = 0
stops_name_to_num = {}

# Graph configuration constants
BUS_AND_STOPS_SCALE = 20
PASS_TOTAL_ARRIVAL_TIME = 3600     # In secs
LOGGING_LEVEL = logging.INFO

test_scenario = 300
cl_enabled = True

if test_scenario == 3:
  ODM_FILE = 'utils/odm3small.csv'
  ROUTES_FILE = 'utils/routes3.csv'
if test_scenario == 30:
  ODM_FILE = 'utils/odm30.csv'
  ROUTES_FILE = 'utils/routes30.csv'
if test_scenario == 300:
  ODM_FILE = 'utils/odm300.csv'
  ROUTES_FILE = 'utils/routes300.csv'

STOP_MAX_PASS = 10000

# Masivo fixed constants, DO NOT MODIFY !!!!
PASS_DATA_FORMAT = 'HHHHL'     # (alight_time, arrival_time, dest_stop, orig_stop, pass_id)
PASS_TYPE = np.dtype([('pass_id', 'u4'), ('orig_stop', 'u2'), ('dest_stop', 'u2'),
                      ('arrival_time', 'u2'), ('alight_time', 'u2'), ('status', 'u1')])
spl_type = np.dtype((PASS_TYPE, (STOP_MAX_PASS)))
spsl_type = np.dtype([('total', 'u4'), ('last_empty', 'u4'), ('w_index', 'u4'), ('spl', spl_type)])

STOP_BUS_WINDOW_DISTANCE = 10




PASS_STATUS_EMPTY_255 = 255
PASS_STATUS_EMPTY = 0
PASS_STATUS_TO_ARRIVE = 1
PASS_STATUS_ARRIVED = 2
PASS_STATUS_IN_BUS = 3
PASS_STATUS_ALIGHTED = 4