import numpy as np
import csv
import os
import globalConstants
from struct import *


def passengers_results(stops_list, buses_list):
    # Create output folders if not exist
    if not os.path.exists(os.path.join(globalConstants.RESULTS_FOLDER_NAME)):
        os.makedirs(os.path.join(globalConstants.RESULTS_FOLDER_NAME))

    file_name = os.path.join(globalConstants.RESULTS_FOLDER_NAME,
                             globalConstants.PASSENGERS_ALIGHTED_FILE_NAME)

    file = open(file_name, 'w', encoding='utf-8')
    field_names = ['pass_id', 'orig_stop', 'dest_stop', 'arrival_time', 'alight_time',
                   'status_num', 'status_text']
    csv_writer = csv.DictWriter(file, fieldnames=field_names, dialect=csv.excel, lineterminator='\n')
    csv_writer.writeheader()

    total_pass = []
    commute_time = []

    for stop in stops_list:
        for pass_pack in stop.pass_alight_list:
            (alight_time, arrival_time, dest_stop, orig_stop, pass_id) = \
                unpack(globalConstants.PASS_DATA_FORMAT, pass_pack)

            csv_writer.writerow({
                'pass_id': str(pass_id),
                'orig_stop': str(orig_stop),
                'dest_stop': str(dest_stop),
                'arrival_time': str(arrival_time),
                'alight_time': str(alight_time),
                'status_num': str(4),
                'status_text': globalConstants.STATUS_TEXT_ARRAY[4]
            })
            commute_time.append(int(alight_time) - int(arrival_time))


    if len(commute_time):
        avg_commute_time = float(sum(commute_time)) / float(len(commute_time))
    else:
        avg_commute_time = 0

    print("Average commute time %f s" % avg_commute_time)

    file.close()


