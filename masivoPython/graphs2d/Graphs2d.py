from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import csv


class Graphs2d:

  def filter_low_pass(self, x):
    fOrder = 3
    normal_cutoff = 0.01
    b, a = butter(fOrder, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, x)

    return y

  def speed_up(self, speed_up_data):

    if len(speed_up_data) <= 2:
      return

    fig, ax = plt.subplots()
    ax.plot(speed_up_data["time"], speed_up_data["speed_up"])
    ax.plot(speed_up_data["time"], self.filter_low_pass(speed_up_data["speed_up"]))

    ax.set(xlabel='time (s)', ylabel='Speed up',
           title='Simulation speed up')
    ax.grid()
    #ax.set_yscale('log')

    fig.savefig("speed_up.eps")
    #plt.show()

  def save_speed_up_csv(self, speed_up_data):

    if len(speed_up_data) <= 2:
      return


    filtered_data = self.filter_low_pass(speed_up_data["speed_up"])

    file = open('speed_up.csv', 'w', encoding='utf-8')
    field_names = ["time (s)", "Speed up", "Speed up filtered"]
    csv_writer = csv.DictWriter(file, fieldnames=field_names, dialect=csv.excel, lineterminator='\n')
    csv_writer.writeheader()

    for i in range(0, len(speed_up_data['time'])):
      csv_writer.writerow({'time (s)': str(speed_up_data['time'][i]),
                           'Speed up': str(speed_up_data['speed_up'][i]),
                           'Speed up filtered': str(filtered_data[i])})

    file.close()
