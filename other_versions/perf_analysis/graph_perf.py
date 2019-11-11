import csv
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os

fileToOpen = sys.argv[1]

END_SIM_TIME = 3600 * 10

with open(fileToOpen) as csv_file:
    num_cu_array = []
    pst_array = []
    suf_array = []
    rtf_array = []
    ef_array = []
    sst = 0

    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            num_cu = float(row[0])
            pst = float(row[1])

            if num_cu == 1:
                sst = pst
            num_cu_array.append(num_cu)
            pst_array.append(pst)

            suf_array.append(sst/pst)
            rtf_array.append(END_SIM_TIME / pst)
            ef_array.append((sst/num_cu)/pst)

            line_count += 1

    # Plot simulation time
    ax = plt.gca()
    plt.plot(num_cu_array, pst_array)

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    [ymin, ymax] = ax.get_ylim()
    ax.set_ylim(0, ymax)

    ax.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

    plt.xlabel("Compute units")
    plt.ylabel("Simulation execution time (s)")
    plt.tight_layout()

    os.path.splitext(fileToOpen)[0]
    plt.savefig(os.path.splitext(fileToOpen)[0] + '_sim_time.eps')
    plt.close()

    # Plot efficiency
    ax = plt.gca()
    plt.plot(num_cu_array, ef_array)

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    [ymin, ymax] = ax.get_ylim()
    ax.set_ylim(0, ymax)

    ax.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

    plt.xlabel("Compute units")
    plt.ylabel("Efficiency")
    plt.tight_layout()

    os.path.splitext(fileToOpen)[0]
    plt.savefig(os.path.splitext(fileToOpen)[0] + '_efficiency.eps')
    plt.close()


    # Plot speed up factor
    ax = plt.gca()
    plt.plot(num_cu_array, suf_array)

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    [ymin, ymax] = ax.get_ylim()
    ax.set_ylim(0, ymax)

    ax.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

    plt.xlabel("Compute units")
    plt.ylabel("Speed up factor")
    plt.tight_layout()

    os.path.splitext(fileToOpen)[0]
    plt.savefig(os.path.splitext(fileToOpen)[0] + '_suf.eps')
    plt.close()

    # Plot real-time factor
    ax = plt.gca()
    plt.plot(num_cu_array, rtf_array)

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    [ymin, ymax] = ax.get_ylim()
    ax.set_ylim(0, ymax)

    ax.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

    plt.xlabel("Compute units")
    plt.ylabel("Real-time factor")
    plt.tight_layout()

    os.path.splitext(fileToOpen)[0]
    plt.savefig(os.path.splitext(fileToOpen)[0] + '_rtf.eps')
    plt.close()