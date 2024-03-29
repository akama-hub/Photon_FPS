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
# motions = ["curb"]

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
                    lag = float(row[8]) * 1000

                    if lag in key:
                        cnt[lag] += 1
                    else:
                        cnt[lag] = 1
                        key.append(lag)

            np_lag = np.sort(np.array(key))
            np_cnt = np.array([cnt[key] for key in np_lag])

            # plt.plot(np_lag, np_cnt)

            # plt.xlabel("Delay [ms]")
            # plt.ylabel("Count")

            # plt.show()
            # plt.savefig(f"evaluate/Figure/CFD_lag/Count_delay{delay}_{motion}_ms.png", bbox_inches='tight', pad_inches=0)
            # plt.savefig(f"evaluate/Figure/CFD_lag/Count_delay{delay}_{motion}.eps", bbox_inches='tight', pad_inches=0)
            
            # plt.clf()
            # plt.close()
            
            
            # print(np_cnt)
            print(np.sum(np_cnt))
            print(len(np_cnt))

            np_cfd = np.array([np_cnt[0]])
            for i in range(1, len(np_cnt)):
                np_cnt[i] = np_cnt[i] + np_cnt[i-1]
                np_cfd = np.append(np_cfd, np_cnt[i])

            # print(np_cfd)
            print(np_cfd[-1])
            
            plt.plot(np_lag, np_cfd/np_cfd[-1])

            plt.xlabel("latency [ms]")
            plt.ylabel("CFD")
            
            # plt.show()
            plt.savefig(f"evaluate/Figure/CFD_lag/delay{delay}_{motion}.png", bbox_inches='tight', pad_inches=0)
            plt.savefig(f"evaluate/Figure/CFD_lag/delay{delay}_{motion}.eps", bbox_inches='tight', pad_inches=0)

            plt.clf()
            plt.close()

        elif flag == "fps":
            with open(log_file)as f:
                reader = csv.reader(f)
                for row in reader:
                    fps = float(row[15]) * 1000

                    if fps in key:
                        cnt[fps] += 1
                    else:
                        cnt[fps] = 1
                        key.append(fps)

            np_fps = np.sort(np.array(key))
            # print(np_fps)
            # print(len(np_fps))
            np_cnt = np.array([cnt[key] for key in np_fps])

            # plt.plot(np_fps, np_cnt)

            # plt.xlabel("Second Per Frame [ms]")
            # plt.ylabel("Count")

            # plt.show()
            # plt.savefig(f"evaluate/Figure/CFD_FPS/Count_delay{delay}_{motion}_ms.png", bbox_inches='tight', pad_inches=0)
            # plt.savefig(f"evaluate/Figure/CFD_FPS/Count_delay{delay}_{motion}.eps", bbox_inches='tight', pad_inches=0)
            
            # plt.clf()
            
            # print(np_cnt)
            # print(np.sum(np_cnt))
            # print(len(np_cnt))
            
            np_cfd = np.array([np_cnt[0]])
            for i in range(1, len(np_cnt)):
                # print(i)
                np_cnt[i] = np_cnt[i] + np_cnt[i-1]
                np_cfd = np.append(np_cfd, np_cnt[i])

            # print(len(np_cfd))
            print(np_cfd[-1])
            print(np_cfd)
            
            plt.plot(np_fps, np_cfd/np_cfd[-1])

            plt.xlabel("milliSeconds per frame update[ms]")
            plt.ylabel("CFD")

            # plt.show()
            plt.savefig(f"evaluate/Figure/CFD_FPS/FPS_delay{delay}_{motion}.png", bbox_inches='tight', pad_inches=0)
            plt.savefig(f"evaluate/Figure/CFD_FPS/FPS_delay{delay}_{motion}.eps", bbox_inches='tight', pad_inches=0)

            plt.clf()
            plt.close()