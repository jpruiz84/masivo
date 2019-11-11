from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import csv
import globalConstants
import numpy as np
import os


class Graphs2d:

    def make_patch_spines_invisible(self, ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
            sp.set_visible(False)

    def filter_low_pass(self, x):
        fOrder = 3
        normal_cutoff = 0.2
        b, a = butter(fOrder, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, x)

        return y

    def performance_graph(self, perf_data, total_executed_time):
        print("\nAverage real-time factor: %d, average CPU usage: %.2f%%" % (
            np.mean(perf_data["rtf"]),
            np.mean(perf_data["cpu_usage"])))

        globalConstants.results['Average_real_time_factor'] = '{:0.2f}'.format(np.mean(perf_data["rtf"]))
        globalConstants.results['Average_cpu_usage'] = '{:0.2f}'.format(np.mean(perf_data["cpu_usage"]))

        if len(perf_data["time"]) <= 10:
            return

        fig, ax = plt.subplots()
        fig.subplots_adjust(right=0.75)

        ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
        ax3 = ax.twinx()  # instantiate a second axes that shares the same x-axis

        p1, = ax.plot(perf_data["time"], perf_data["rtf"], label='RTF not filtered')
        p2, = ax.plot(perf_data["time"], self.filter_low_pass(perf_data["rtf"]),
                      label='RTF low-pass filtered')

        ax.set(xlabel='Simulation time (s)', ylabel='Real-time factor (RTF)')
        # ax.set_yscale('log')
        [ymin, ymax] = ax.get_ylim()
        ax.set_ylim(0, ymax)

        [xmin, xmax] = ax.get_xlim()
        ax.set_xlim(0, xmax)

        # Offset the right spine of par2.  The ticks and label have already been
        # placed on the right by twinx above.
        ax3.spines["right"].set_position(("axes", 1.2))
        # Having been created by twinx, par2 has its frame off, so the line of its
        # detached spine is invisible.  First, activate the frame but make the patch
        # and spines invisible.
        self.make_patch_spines_invisible(ax3)
        # Second, show the right spine.
        ax3.spines["right"].set_visible(True)

        p3, = ax2.plot(perf_data["time"], self.filter_low_pass(perf_data["cpu_usage"]), label='CPU usage',
                 color='tab:green')

        ax2.set_ylim(0, 110)
        ax2.set_ylabel('CPU usage (%)')

        p4, = ax3.plot(perf_data["time"], self.filter_low_pass(perf_data["cpu_freq"]), label='CPU frequency',
                 color='tab:red')
        ax3.set_ylabel('CPU frequency (KHz)')
        ax3.set_ylim(0, 5000)



        #ax.set(title='Performance, for %d stops' % len(stops_list))

        lines = [p1, p2, p3, p4]

        ax.set_zorder(4)  # put ax in front of ax2
        ax.patch.set_visible(False)  # hide the 'canvas'
        ax2.set_zorder(3)  # put ax in front of ax2
        ax2.patch.set_visible(False)  # hide the 'canvas'
        ax3.set_zorder(2)  # put ax in front of ax2
        ax3.patch.set_visible(False)  # hide the 'canvas'

        ax.grid(linestyle='--', linewidth=0.5, dashes=(5, 10), zorder=1)

        footnote = ("Total sim. execution time: %0.3f s" % (total_executed_time))
        plt.figtext(0.99, 0.01, footnote, wrap=True, horizontalalignment='right', fontsize=9)

        ax.legend(lines, [l.get_label() for l in lines], loc='upper center',
                   bbox_to_anchor=(0.5, 1.11), fontsize=9, ncol=2, fancybox=True, shadow=True)


        plt.tight_layout()

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
        field_names = ["time (s)", "RTF", "RTF filtered", "CPU usage (%)", "CPU freq (KHz)"]
        csv_writer = csv.DictWriter(file, fieldnames=field_names, dialect=csv.excel, lineterminator='\n')
        csv_writer.writeheader()

        for i in range(0, len(perf_data['time'])):
            csv_writer.writerow({'time (s)': str(perf_data['time'][i]),
                                 'RTF': '{:0.2f}'.format(perf_data['rtf'][i]),
                                 'RTF filtered': '{:0.2f}'.format(filtered_data[i]),
                                 'CPU usage (%)': perf_data['cpu_usage'][i],
                                 'CPU freq (KHz)': int(perf_data['cpu_freq'][i])
                                 })

        file.close()

    def commute_time(self, pass_list):
        # Create output folders if not exist

        total_commute_time = []
        stop_ct_we_array = []
        stop_ct_ew_array = []
        for stops in pass_list:
            commute_time_we = []
            commute_time_ew = []
            for pass_data in stops['spl']:
                if pass_data['status'] == globalConstants.PASS_STATUS_ALIGHTED:
                    diff_time = int(pass_data['alight_time']) - int(pass_data['arrival_time'])
                    if pass_data['orig_stop'] < pass_data['dest_stop']:
                        commute_time_we.append(diff_time)
                    else:
                        commute_time_ew.append(diff_time)
                    total_commute_time.append(diff_time)

            if len(commute_time_we):
                avg_commute_time = float(sum(commute_time_we)) / float(len(commute_time_we))
            else:
                avg_commute_time = 0
            stop_ct_we_array.append(avg_commute_time / 60)

            if len(commute_time_ew):
                avg_commute_time = float(sum(commute_time_ew)) / float(len(commute_time_ew))
            else:
                avg_commute_time = 0
            stop_ct_ew_array.append(avg_commute_time / 60)

        if len(total_commute_time):
            avg_total_commute_time = float(sum(total_commute_time)) / float(len(total_commute_time))
        else:
            avg_total_commute_time = 0

        print("Average total commute time %f s" % avg_total_commute_time)
        globalConstants.results['Total_average_commute_time'] = \
            '{:0.3f}'.format(avg_total_commute_time)


        width = 0.35  # the width of the bars

        x = np.arange(len(stop_ct_ew_array))  # the label location
        fig, ax = plt.subplots()
        ax.yaxis.grid(linestyle='--', linewidth=0.5, dashes=(5, 10), zorder=1)

        ax.bar(x - width / 2, stop_ct_we_array, width, label='W-E', zorder=2)
        ax.bar(x + width / 2, stop_ct_ew_array, width, label='E-W', zorder=2)

        ax.set(xlabel='Stop number', ylabel='Average commute time (min)',
               title='Commute time per dest. stop ')
        ax.legend(title="Pass. direc.", loc='lower right', fontsize=9)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        footnote = ("Total avg. comm. time: %0.2f min" % (avg_total_commute_time / 60.0))
        plt.figtext(0.99, 0.01, footnote, wrap=True, horizontalalignment='right', fontsize=9)

        plt.tight_layout()
        # plt.show()
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
                'alighted percentage (%)':
                    '{:0.2f}'.format(100.0 * stop.pass_alight_count() / stop.expected_alight_pass)
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

        globalConstants.results['Total_alighted_passengers'] = total_alighted_pass
        globalConstants.results['Total_alighted_expected_passengers'] = total_expected_alighted_pass
        globalConstants.results['Total_alighted_passengers_percentage'] = \
            '{:0.2f}'.format(100.0 * total_alighted_pass / total_expected_alighted_pass)

        width = 0.5  # the width of the bars

        x = np.arange(len(pass_waiting))
        fig, ax = plt.subplots()

        ax.yaxis.grid(linestyle='--', linewidth=0.5, dashes=(5, 10), zorder=1)
        ax.bar(x, pass_alighted, width, label='Alighted', zorder=2)
        ax.bar(x, pass_not_alighted, width, bottom=pass_alighted, label='Not alighted', zorder=2)
        ax.set(xlabel='Stop number', ylabel='Number of passengers', title='Destination stop passengers')

        footnote = ("Total alighted: %d/%d, %.2f%%" % (total_alighted_pass,
                                                       total_expected_alighted_pass,
                                                       100.0 * total_alighted_pass / total_expected_alighted_pass))
        plt.figtext(0.99, 0.01, footnote, wrap=True, horizontalalignment='right', fontsize=9)

        [ymin, ymax] = ax.get_ylim()
        ax.set_ylim(0, ymax*1.1)

        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(fontsize=9)
        plt.tight_layout()

        fig.savefig(os.path.join(globalConstants.RESULTS_FOLDER_NAME,
                                 globalConstants.GRAPH_SERVED_PASSENGERS_FILE_NAME))
        #plt.show()
        plt.close()

        print('')
