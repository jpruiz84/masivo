import logging

# Global variables
pass_num = 0
stops_name_to_num = {}

# Graph configuration constants
BUS_AND_STOPS_SCALE = 20
PASS_TOTAL_ARRIVAL_TIME = 3600     # In secs
LOGGING_LEVEL = logging.ERROR

test_scenario = 30

if test_scenario == 3:
  ODM_FILE = 'utils/odm3.csv'
  ROUTES_FILE = 'utils/routes3.csv'
if test_scenario == 30:
  ODM_FILE = 'utils/odm30.csv'
  ROUTES_FILE = 'utils/routes30.csv'

# Masivo fixed constants, DO NOT MODIFY !!!!
PASS_DATA_FORMAT = 'HHHHL'     # (alight_time, arrival_time, dest_stop, orig_stop, pass_id)
STOP_BUS_WINDOW_DISTANCE = 10
