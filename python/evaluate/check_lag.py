import numpy as np
import csv
import math
import statistics

delay = []
# second0 = 0
# lags = [0, 20, 40]
lags = [0, 10, 20, 30, 40]

for lag in lags:
    # with open(f"chamfer/Fixed30FPS_SendRate60_RTT/Lag{lag}/ohuku/DRL_distance/Delayed_log.csv")as f:
    with open(f"lagAVG/Fixed30FPS_SendRate60_RTT/Lag{lag}/check_log_1217.csv")as f:
        reader = csv.reader(f)
        for row in reader:
            # delay.append(float(row[8])*1000)
            # delay.append(float(row[15])*1000) #fps
            delay.append(float(row[1])*1000)

    print("lag: ", lag)
    print("delay avg.: ", sum(delay) / len(delay))
    print("minimum: ", min(delay))
    print("maximum: ", max(delay))
    print("variance: ", statistics.variance(delay))
    print("=====================================")
            