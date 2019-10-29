import numpy as np
import csv
import os
import globalConstants


def pass_alight(pass_list):
    # Create output folders if not exist
    if not os.path.exists(os.path.join(globalConstants.RESULTS_FOLDER)):
        os.makedirs(os.path.join(globalConstants.RESULTS_FOLDER))

    file_name = os.path.join(globalConstants.RESULTS_FOLDER, 'pass_alight.csv')

    file = open(file_name, 'w', encoding='utf-8')
    field_names = globalConstants.PASS_TYPE.names
    csv_writer = csv.DictWriter(file, fieldnames=field_names, dialect=csv.excel, lineterminator='\n')
    csv_writer.writeheader()

    commute_time = []

    for stops in pass_list:
        for pass_data in stops['spl']:
            if pass_data['status'] == globalConstants.PASS_STATUS_ALIGHTED:
                csv_writer.writerow({
                    'pass_id': str(pass_data['pass_id']),
                    'orig_stop': str(pass_data['orig_stop']),
                    'dest_stop': str(pass_data['dest_stop']),
                    'arrival_time': str(pass_data['arrival_time']),
                    'alight_time': str(pass_data['alight_time']),
                    'status': str(pass_data['status'])})

                commute_time.append(int(pass_data['alight_time']) - int(pass_data['arrival_time']))

    if len(commute_time):
        avg_commute_time = float(sum(commute_time)) / float(len(commute_time))
    else:
        avg_commute_time = 0

    print("Average commute time %f s" % avg_commute_time)

    file.close()
