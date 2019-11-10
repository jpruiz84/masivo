import numpy as np
import csv
import os
import globalConstants


def passengers_results(stops_hanlder, buses_handler):
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

    for stops in stops_hanlder.get_stops_arrival_list():
        for pass_data in stops['spl']:
            if pass_data['status'] == globalConstants.PASS_STATUS_TO_ARRIVE:
                total_pass.append(pass_data)

    for stops in stops_hanlder.get_stops_queue_list():
        for pass_data in stops['spl']:
            if pass_data['status'] == globalConstants.PASS_STATUS_ARRIVED:
                total_pass.append(pass_data)

    for stops in stops_hanlder.get_stops_alight_list():
        for pass_data in stops['spl']:
            if pass_data['status'] == globalConstants.PASS_STATUS_ALIGHTED:
                total_pass.append(pass_data)
                commute_time.append(int(pass_data['alight_time']) - int(pass_data['arrival_time']))

    for bus in buses_handler.get_final_bus_struc_list():
        for pass_data in bus['bpl']:
            if pass_data['status'] == globalConstants.PASS_STATUS_IN_BUS:
                total_pass.append(pass_data)

    for pass_data in total_pass:
        csv_writer.writerow({
            'pass_id': str(pass_data['pass_id']),
            'orig_stop': str(pass_data['orig_stop']),
            'dest_stop': str(pass_data['dest_stop']),
            'arrival_time': str(pass_data['arrival_time']),
            'alight_time': str(pass_data['alight_time']),
            'status_num': str(pass_data['status']),
            'status_text': globalConstants.STATUS_TEXT_ARRAY[pass_data['status']]
        })
    if len(commute_time):
        avg_commute_time = float(sum(commute_time)) / float(len(commute_time))
    else:
        avg_commute_time = 0

    print("Average commute time %f s" % avg_commute_time)

    file.close()


