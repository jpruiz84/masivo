from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt



class Graphs2d:

  def filter_low_pass(self, x,):
    fOrder = 3
    normal_cutoff = 0.01
    b, a = butter(fOrder, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, x)

    return y

  def speed_up(self, speed_up_data):
    fig, ax = plt.subplots()
    ax.plot(speed_up_data["time"], speed_up_data["speed_up"])
    ax.plot(speed_up_data["time"], self.filter_low_pass(speed_up_data["speed_up"]))

    ax.set(xlabel='time (s)', ylabel='Speed up',
           title='Simulation speed up')
    ax.grid()

    fig.savefig("speed_up.png")
    plt.show()