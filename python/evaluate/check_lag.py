import numpy as np
import csv
import math
import statistics

delay = []
# second0 = 0
lags = [0, 20, 40]

for lag in lags:
    with open(f"chamfer/Fixed30FPS_SendRate60_RTT/Lag{lag}/ohuku/DRL_distance/Delayed_log.csv")as f:
        reader = csv.reader(f)
        for row in reader:
            # delay.append(float(row[8]))
            delay.append(float(row[15])) #fps

    print("lag: ", lag)
    print("delay avg.: ", sum(delay) / len(delay))
    print("minimum: ", min(delay))
    print("maximum: ", max(delay))
    print("variance: ", statistics.variance(delay))
    print("=====================================")
            