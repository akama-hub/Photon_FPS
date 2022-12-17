import numpy as np
import matplotlib.pyplot as plt
import os

plt.rcParams["font.size"] = 20
# plt.rcParams["legend.labelspacing"] = 0
plt.rcParams["font.family"] = 'Times New Roman'
plt.figure(figsize = (8.0, 6.0))
markers = ["o", "v", "s", ">", "<"]
colors = ["r", "b", "g", "c", "m", "y", "k"]

marker_size = 12

# motions = ["ohuku", "ohukuRandom"]
motions = ["ohuku"]

fire_count = 50

for motion in motions:
    pic_dir = f"figure/"
    os.makedirs(pic_dir, exist_ok=True)

    # Lag = [0, 10, 25] # Photon lag simulation gui paramater(ms)
    # Lag = [0, 10, 20, 30, 40]
    Lag = [41.7, 50.7, 61.1, 71.3, 81.4]

    if motion == "ohuku":
        # hit_count = np.array([2, 0, 0])
        # DR_hit_count = np.array([50, 33, 3])
        # MAADR_hit_count = np.array([49, 30, 0])
        # proposed_hit_count = np.array([44, 33, 25])
        DR_hit_count = np.array([100, 96, 58, 1, 0])
        MAADR_hit_count = np.array([100, 98, 33, 1, 1])
        proposed_hit_count = np.array([96, 75, 50, 49, 44])

    elif motion == "ohukuRandom":
        hit_count = np.array([2, 0, 0])
        DR_hit_count = np.array([18, 3, 1])
        proposed_hit_count = np.array([43, 33, 23])

    # hit_rate = hit_count / 50
    # DR_hit_rate = DR_hit_count / 50
    # MAADR_hit_rate = MAADR_hit_count / 50
    # proposed_hit_rate = proposed_hit_count / 50
    
    DR_hit_rate = DR_hit_count / 100
    MAADR_hit_rate = MAADR_hit_count / 100
    proposed_hit_rate = proposed_hit_count / 100

    print("===========================")
    print(f"making hit rate png & eps graph")

    p1 = plt.plot(Lag, DR_hit_rate, linestyle = "--", dashes = (4, 4), marker='x', color = colors[2], markerfacecolor = "None", ms = marker_size)
    p2 = plt.plot(Lag, MAADR_hit_rate, linestyle = "--", dashes = (5, 5), marker=markers[2], color = "grey", markerfacecolor = "None", ms = marker_size)
    p3 = plt.plot(Lag, proposed_hit_rate, linestyle = "--", dashes = (7, 7), marker='*', color = colors[0], markerfacecolor = "None", ms = marker_size)

    plt.xlabel("Latency avg. [ms]")
    # plt.ylabel("Hit Rate ")
    plt.ylabel("Match Rate of Hit Result Decision")

    plt.legend((p1[0], p2[0], p3[0]), ("DR", "MAADR", "Proposed"))

    plt.savefig(f"figure/{motion}_HitRate_avg.png", bbox_inches='tight', pad_inches=0)
    plt.savefig(f"figure/{motion}_HitRate_avg.eps", bbox_inches='tight', pad_inches=0)

    plt.clf()
    plt.close()