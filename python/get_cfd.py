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

delays = [0, 20, 40]
motions = ["ohuku"]

flag = "fps"
# flag = "lag"

for delay in delays:
    for motion in motions:
        log_file = f"evaluate/chamfer/Fixed30FPS_SendRate60_RTT/Lag{delay}/{motion}/DRL_distance/Delayed_log.csv"

        cnt = {}
        key = []

        if flag == "lag":
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

            # plt.plot(np_lag, np_cnt)

            # plt.xlabel("Delay [s]")
            # plt.ylabel("Count")

            # plt.show()
            # plt.savefig(f"evaluate/Figure/CFD/Count_delay{delay}_{motion}.png", bbox_inches='tight', pad_inches=0)

            np_cfd = np.array([np_cnt[0]])
            for i in range(1, len(np_cnt)):
                np_cnt[i] = np_cnt[i] + np_cnt[i-1]
                np_cfd = np.append(np_cfd, np_cnt[i])

            # print(np_cfd)

            
            plt.plot(np_lag, np_cfd)

            plt.xlabel("Delay [s]")
            plt.ylabel("CFD")

            plt.show()
            plt.savefig(f"evaluate/Figure/CFD/delay{delay}_{motion}.png", bbox_inches='tight', pad_inches=0)

            plt.clf()
            plt.close()

        elif flag == "fps":
            with open(log_file)as f:
                reader = csv.reader(f)
                for row in reader:
                    fps = float(row[15])

                    if fps in key:
                        cnt[fps] += 1
                    else:
                        cnt[fps] = 1
                        key.append(fps)

            np_fps = np.sort(np.array(key))
            np_cnt = np.array([cnt[key] for key in np_fps])

            plt.plot(np_fps, np_cnt)

            plt.xlabel("Delay [s]")
            plt.ylabel("Count")

            plt.show()
            plt.savefig(f"evaluate/Figure/CFD_FPS/Count_delay{delay}_{motion}.png", bbox_inches='tight', pad_inches=0)

            # np_cfd = np.array([np_cnt[0]])
            # for i in range(1, len(np_cnt)):
            #     np_cnt[i] = np_cnt[i] + np_cnt[i-1]
            #     np_cfd = np.append(np_cfd, np_cnt[i])

            # # print(np_cfd)

            
            # plt.plot(np_fps, np_cfd)

            # plt.xlabel("Delay [s]")
            # plt.ylabel("CFD")

            # plt.show()
            # plt.savefig(f"evaluate/Figure/CFD_FPS/delay{delay}_{motion}.png", bbox_inches='tight', pad_inches=0)

            plt.clf()
            plt.close()