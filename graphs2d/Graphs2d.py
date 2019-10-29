from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import csv
import globalConstants

class Graphs2d:

    def filter_low_pass(self, x):
        fOrder = 3
        normal_cutoff = 0.01
        b, a = butter(fOrder, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, x)

        return y

    def real_time_factor_graph(self, rtf_data):
        if len(rtf_data["time"]) <= 2:
            return

        fig, ax = plt.subplots()
        ax.plot(rtf_data["time"], rtf_data["factor"])
        ax.plot(rtf_data["time"], self.filter_low_pass(rtf_data["factor"]))

        ax.set(xlabel='time (s)', ylabel='Real time factor')
        ax.grid()
        # ax.set_yscale('log')

        if globalConstants.USE_PYOPENCL:
            ax.set(title='RTF using PythonCL')
            fig.savefig("pyopencl_rtf.eps")
        elif globalConstants.USE_PYTHON_C:
            ax.set(title='RTF using PythonC')
            fig.savefig("pythonc_rtf.eps")
        elif globalConstants.USE_PYTHON:
            ax.set(title='RTF using pure python')
            fig.savefig("pure_python_rtf.eps")


        # plt.show()

    def save_speed_up_csv(self, rtf_data):

        if len(rtf_data["time"]) <= 2:
            return

        filtered_data = self.filter_low_pass(rtf_data["factor"])

        file = open('rtf.csv', 'w', encoding='utf-8')
        field_names = ["time (s)", "RTF", "RTF filtered"]
        csv_writer = csv.DictWriter(file, fieldnames=field_names, dialect=csv.excel, lineterminator='\n')
        csv_writer.writeheader()

        for i in range(0, len(rtf_data['time'])):
            csv_writer.writerow({'time (s)': str(rtf_data['time'][i]),
                                 'RTF': str(rtf_data['factor'][i]),
                                 'RTF filtered': str(filtered_data[i])})

        file.close()
