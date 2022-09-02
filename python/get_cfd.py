import numpy as np
import csv
import math
import statistics

import numpy as np
import matplotlib.pyplot as plt

fps = []
flag = 0
except_count = 0
# second0 = 0

log_file = "evaluate/chamfer/Fixed30FPS_SendRate60_RTT/Lag20/ohuku/DRL_distance/Delayed_log.csv"
cfd = {}
key = []

with open(log_file)as f:
    reader = csv.reader(f)
    for row in reader:
        lag = float(row[1])
        if lag in key:
            cfd[lag] += 1
        else:
            cfd[lag] = 1
            key.append(lag)

np_lag = np.sort(np.array(lag))
np_cfd = np.array([cfd[key] for key in np_lag])

plt.plot(np_lag, np_cfd)
plt.show()

# print("lag avg.: ", sum(fps) / len(fps))
# print("minimum: ", min(fps))
# print("maximum: ", max(fps))
# print("variance: ", statistics.variance(fps))
# # print("0 count: ", second0)
# print("Except count: ", except_count)
        