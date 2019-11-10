from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import csv
import globalConstants
import numpy as np
from matplotlib.ticker import MaxNLocator
import os


class Graphs2d:

    def filter_low_pass(self, x):
        fOrder = 3
        normal_cutoff = 0.2
        b, a = butter(fOrder, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, x)

        return y

    def performance_graph(self, perf_data, stops_list):

        print("\nAverage real-time factor: %d, average CPU usage: %.2f%%" % (
            np.mean(perf_data["rtf"]),
            np.mean(perf_data["cpu_usage"])))

        if len(perf_data["time"]) <= 10:
            return

        fig, ax = plt.subplots()
        ax.plot(perf_data["time"], perf_data["rtf"], label='Not filtered')
        ax.plot(perf_data["time"], self.filter_low_pass(perf_data["rtf"]), label='Low pass filtered')

        ax.set(xlabel='Simulation time (s)', ylabel='Real-time factor')
        ax.grid()
        # ax.set_yscale('log')
        [ymin, ymax] = ax.get_ylim()
        ax.set_ylim(0, ymax)



        ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(perf_data["time"], self.filter_low_pass(perf_data["cpu_usage"]), label='CPU usage',
                 color = 'tab:green')

        ax2.set_ylim(0, 110)
        ax2.set_ylabel('CPU usage (%)')

        ax.legend(loc='lower left')
        ax2.legend(loc='lower right')

        if globalConstants.USE_PYOPENCL:
            ax.set(title='Performance using PythonCL, for %d stops' % len(stops_list))
        elif globalConstants.USE_PYTHON_C:
            ax.set(title='Performance using PythonC, for %d stops' % len(stops_list))
        elif globalConstants.USE_PYTHON:
            ax.set(title='Performance using pure python, for %d stops' % len(stops_list))

        fig.savefig(os.path.join(globalConstants.RESULTS_FOLDER_NAME,
                                 globalConstants.GRAPH_PERFORMANCE_TIMELINE_FILE_NAME))

        #plt.show()
        plt.close()


    def save_performance_csv(self, perf_data):

        if len(perf_data["time"]) <= 10:
            return

        filtered_data = self.filter_low_pass(perf_data["rtf"])

        filename = (os.path.join(globalConstants.RESULTS_FOLDER_NAME,
                             globalConstants.CSV_PERFORMANCE_TIMELINE_FILE_NAME))

        file = open(filename, 'w', encoding='utf-8')
        field_names = ["time (s)", "RTF", "RTF filtered", "CPU usage (%)"]
        csv_writer = csv.DictWriter(file, fieldnames=field_names, dialect=csv.excel, lineterminator='\n')
        csv_writer.writeheader()

        for i in range(0, len(perf_data['time'])):
            csv_writer.writerow({'time (s)': str(perf_data['time'][i]),
                                 'RTF': '{:0.2f}'.format(perf_data['rtf'][i]),
                                 'RTF filtered': '{:0.2f}'.format(filtered_data[i]),
                                 'CPU usage (%)': perf_data['cpu_usage'][i]
                                 })

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
        ax.legend(title="Pass. direc.", loc='lower right')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        #plt.show()

        fig.savefig(os.path.join(globalConstants.RESULTS_FOLDER_NAME,
                                 globalConstants.GRAPH_COMMUTE_TIME_PER_STOP_FILE_NAME))

        plt.close()

    def served_passengers(self, stops_list):
        # Create output folders if not exist

        file_name = os.path.join(globalConstants.RESULTS_FOLDER_NAME,
                                 globalConstants.PASSENGERS_ALIGHTED_PER_STOP_FILE_NAME)

        file = open(file_name, 'w', encoding='utf-8')
        field_names = ['stop num', 'stop name', 'total waiting pass.', 'total expected input pass.',
                       'total alight pass.', 'total expected alight pass.', 'alighted percentage (%)']
        csv_writer = csv.DictWriter(file, fieldnames=field_names, dialect=csv.excel, lineterminator='\n')
        csv_writer.writeheader()

        print('\nStops list:')
        for stop in stops_list:
            print("Stop %s has %d/%d pass,\t  alighted %d/%d, \t %.2f%%" %
                  (stop.name, stop.pass_count(),
                   stop.total_pass_in,
                   stop.pass_alight_count(),
                   stop.expected_alight_pass,
                   100 * stop.pass_alight_count() / stop.expected_alight_pass))


            csv_writer.writerow({
                'stop num': str(stop.number),
                'stop name': str(stop.name),
                'total waiting pass.': str(stop.pass_count()),
                'total expected input pass.': str(stop.total_pass_in),
                'total alight pass.': str(stop.pass_alight_count()),
                'total expected alight pass.': str(stop.expected_alight_pass),
                'alighted percentage (%)': '{:0.2f}'.format(100 * stop.pass_alight_count() / stop.expected_alight_pass)
            })

        file.close()


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

        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend()

        fig.savefig(os.path.join(globalConstants.RESULTS_FOLDER_NAME,
                                 globalConstants.GRAPH_SERVED_PASSENGERS_FILE_NAME))

        #plt.show()

        print('')