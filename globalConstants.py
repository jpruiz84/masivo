import logging

# Global variables
pass_num = 0

# Graph configuration constants
BUS_AND_STOPS_SCALE = 20
PASS_TOTAL_ARRIVAL_TIME = 3600     # In secs
LOGGING_LEVEL = logging.INFO
if 1:
  ODM_FILE = 'utils/odmTest.csv'
  ROUTES_FILE = 'utils/routesTest.csv'
else:
  ODM_FILE = 'utils/odm1.csv'
  ROUTES_FILE = 'utils/routes1.csv'

# Masivo fixed constants, DO NOT MODIFY !!!!
PASS_DATA_FORMAT = 'HHHHL'     # (alight_time, arrival_time, dest_stop, orig_stop, pass_id)
STOP_BUS_WINDOW_DISTANCE = 10
