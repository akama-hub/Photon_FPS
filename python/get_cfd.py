from operator import contains
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
cnt = {}
key = []

with open(log_file)as f:
    reader = csv.reader(f)
    for row in reader:
        lag = float(row[8])
        if lag in key:
            cnt[lag] += 1
        else:
            cnt[lag] = 1
            key.append(lag)

np_lag = np.sort(np.array(key))
np_cnt = np.array([cnt[key] for key in np_lag])

plt.plot(np_lag, np_cnt)

np_cfd = np.array([np_cnt[0]])
for i in range(1, len(np_cnt)):
    np_cnt[i] = np_cnt[i] + np_cnt[i-1]
    np_cfd = np.append(np_cfd, np_cnt[i])

# print(np_cfd)


# plt.plot(np_lag, np_cfd)
plt.show()

        