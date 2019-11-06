from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import csv
import globalConstants
import numpy as np

class Graphs2d:

    def filter_low_pass(self, x):
        fOrder = 3
        normal_cutoff = 0.05
        b, a = butter(fOrder, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, x)

        return y

    def real_time_factor_graph(self, rtf_data):

        print("\nAverage real time factor: %d" % np.mean(rtf_data["factor"]))

        if len(rtf_data["time"]) <= 10:
            return

        fig, ax = plt.subplots()
        ax.plot(rtf_data["time"], rtf_data["factor"])
        ax.plot(rtf_data["time"], self.filter_low_pass(rtf_data["factor"]))

        ax.set(xlabel='time (s)', ylabel='Real time factor')
        ax.grid()
        # ax.set_yscale('log')
        [ymin, ymax] = ax.get_ylim()
        ax.set_ylim(0, ymax)

        if globalConstants.USE_PYOPENCL:
            ax.set(title='RTF using PythonCL')
            fig.savefig("results/pyopencl_rtf_tc_%d.eps" % globalConstants.test_scenario)
        elif globalConstants.USE_PYTHON_C:
            ax.set(title='RTF using PythonC')
            fig.savefig("results/pythonc_rtf_tc_%d.eps" % globalConstants.test_scenario.eps)
        elif globalConstants.USE_PYTHON:
            ax.set(title='RTF using pure python')
            fig.savefig("results/pure_python_rtf_tc_%d.eps" % globalConstants.test_scenario)

        #plt.show()
        plt.close()


    def save_speed_up_csv(self, rtf_data):

        if len(rtf_data["time"]) <= 10:
            return

        filtered_data = self.filter_low_pass(rtf_data["factor"])

        if globalConstants.USE_PYOPENCL:
            filename = ("results/pyopencl_rtf_table_tc_%d.csv" % globalConstants.test_scenario)
        elif globalConstants.USE_PYTHON_C:
            filename = ("results/pyopenc_rtf_table_tc_%d.csv" % globalConstants.test_scenario)
        elif globalConstants.USE_PYTHON:
            filename = ("results/pure_python_rtf_table_tc_%d.csv" % globalConstants.test_scenario)

        file = open(filename, 'w', encoding='utf-8')
        field_names = ["time (s)", "RTF", "RTF filtered"]
        csv_writer = csv.DictWriter(file, fieldnames=field_names, dialect=csv.excel, lineterminator='\n')
        csv_writer.writeheader()

        for i in range(0, len(rtf_data['time'])):
            csv_writer.writerow({'time (s)': str(rtf_data['time'][i]),
                                 'RTF': str(rtf_data['factor'][i]),
                                 'RTF filtered': str(filtered_data[i])})

        file.close()

    def commute_time(self, pass_list):
        # Create output folders if not exist

        stop_ct_we_array = []
        stop_ct_ew_array = []
        for stops in pass_list:
            commute_time_we = []
            commute_time_ew = []
            for pass_data in stops['spl']:
                if pass_data['status'] == globalConstants.PASS_STATUS_ALIGHTED:
                    if pass_data['orig_stop'] < pass_data['dest_stop']:
                        commute_time_we.append(int(pass_data['alight_time']) - int(pass_data['arrival_time']))
                    else:
                        commute_time_ew.append(int(pass_data['alight_time']) - int(pass_data['arrival_time']))

            if len(commute_time_we):
                avg_commute_time = float(sum(commute_time_we)) / float(len(commute_time_we))
            else:
                avg_commute_time = 0
            stop_ct_we_array.append(avg_commute_time/60)

            if len(commute_time_ew):
                avg_commute_time = float(sum(commute_time_ew)) / float(len(commute_time_ew))
            else:
                avg_commute_time = 0
            stop_ct_ew_array.append(avg_commute_time/60)

        width = 0.35  # the width of the bars

        x = np.arange(len(stop_ct_ew_array))  # the label location
        fig, ax = plt.subplots()
        #ax.grid()

        ax.bar(x - width / 2, stop_ct_we_array, width, label='W-E')
        ax.bar(x + width / 2, stop_ct_ew_array, width, label='E-W')

        ax.set(xlabel='Stop number', ylabel='Average commute time (min)')
        ax.legend(title="Passenger direction")

        #plt.show()
        plt.close()

    def served_passengers(self, stops_list):
        # Create output folders if not exist

        print('\nStops list:')
        for stop in stops_list:
            print("Stop %s has %d/%d pass,\t  alighted %d/%d, \t %.2f%%" %
                  (stop.name, stop.pass_count(),
                   stop.total_pass_in,
                   stop.pass_alight_count(),
                   stop.expected_alight_pass,
                   100 * stop.pass_alight_count() / stop.expected_alight_pass))

        # This data comes from stop.pass_count(), stop.total_pass_in
        pass_waiting = []
        pass_boarded = []

        # This data comes from stop.pass_alight_count(), stop.expected_alight_pass
        pass_alighted = []
        pass_not_alighted = []

        total_alighted_pass = 0
        total_expected_alighted_pass = 0

        for stop in stops_list:
            pass_waiting.append(int(stop.pass_count()))
            pass_boarded.append(stop.total_pass_in - stop.pass_count())

            pass_alighted.append(int(stop.pass_alight_count()))
            pass_not_alighted.append(stop.expected_alight_pass - stop.pass_alight_count())

            total_alighted_pass += int(stop.pass_alight_count())
            total_expected_alighted_pass += stop.expected_alight_pass

        print("Total alighted: %d/%d,  %.2f%%" % (total_alighted_pass,
                                                total_expected_alighted_pass,
                                                100.0 * total_alighted_pass / total_expected_alighted_pass))

        width = 0.5  # the width of the bars

        x = np.arange(len(pass_waiting))
        fig, ax = plt.subplots()
        # ax.grid()

        #p1 = ax.bar(x, pass_boarded, width, label='Departed')
        #p2 = ax.bar(x, pass_waiting, width, bottom=pass_boarded, label='Still waiting')
        #ax.set(xlabel='Stop number', ylabel='Number of passengers', title = 'Origin stop passengers')
        #ax.legend()

        p1 = ax.bar(x, pass_alighted, width, label='Alighted')
        p2 = ax.bar(x, pass_not_alighted, width, bottom=pass_alighted, label='Not alighted')
        ax.set(xlabel='Stop number', ylabel='Number of passengers', title = 'Destination stop passengers')
        ax.legend()

        #plt.show()

        print('')