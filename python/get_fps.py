import numpy as np
import csv
import math
import statistics

fps = []
flag = 0
except_count = 0
# second0 = 0

with open("evaluate/chamfer/Fixed30FPS_SendRate60_RTT/Lag20/ohuku/DRL_distance/Delayed_log.csv")as f:
    reader = csv.reader(f)
    for row in reader:
        if flag == 0:
            last_time = float(row[1])
            flag = 1
        else:
            frame_second = float(row[1]) - last_time

            if frame_second >= 0:
                fps.append(frame_second)
            # elif frame_second == 0:
            #     second0 += 1
            else:
                except_count += 1

            last_time = float(row[1])

print("FPS avg.: ", sum(fps) / len(fps))
print("minimum: ", min(fps))
print("maximum: ", max(fps))
print("variance: ", statistics.variance(fps))
# print("0 count: ", second0)
print("Except count: ", except_count)
        