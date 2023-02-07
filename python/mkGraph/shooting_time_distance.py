import numpy as np
import matplotlib.pyplot as plt
import os
import csv

plt.rcParams["font.size"] = 20
# plt.rcParams["legend.labelspacing"] = 0
plt.rcParams["font.family"] = 'Times New Roman'
plt.figure(figsize = (8.0, 6.0))
markers = ["o", "v", "s", ">", "<"]
colors = ["r", "b", "g", "c", "m", "y", "k"]

marker_size = 12

# motions = ["ohuku", "ohukuRandom"]
motions = ["ohuku"]

for motion in motions:
    pic_dir = f"figure/"
    os.makedirs(pic_dir, exist_ok=True)

    # Lag = [0, 10, 25] # Photon lag simulation gui paramater(ms)
    Lag = [0, 10, 20, 30, 40]
    schemes = ["DR", "MAADR", "Propose"]
    
    DR_distance = []
    MAADR_distance = []
    Propose_distance = []
    
    DR_distance_avg = []
    MAADR_distance_avg = []
    Propose_distance_avg = []
    
    for l in Lag:
        for scheme in schemes:
            dir = f"../evaluate/shoot_time_pos/Fixed30FPS_SendRate60_RTT/Lag{l}/{motion}/{scheme}"
            
            real_log_file = f"{dir}/Real_log.csv"
            predict_log_file = f"{dir}/Predict_log.csv"
            
            real_key = []
            real_position = {}
            
            with open(real_log_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    row[0] = int(row[0])
                    for i in range(1,4):
                        row[i] = float(row[i])
                    real_key.append(row[0])
                    real_position[row[0]] = [row[1], row[2], row[3]]
                    
            predict_key = []
            predict_position = {}
            
            with open(predict_log_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    row[0] = int(row[0])
                    for i in range(1,4):
                        row[i] = float(row[i])
                    predict_key.append(row[0])
                    predict_position[row[0]] = [row[1], row[2], row[3]]
                    
            if motion == "ohuku":
                if scheme == "DR":
                    for i in range(100):
                        DR_distance.append(abs(real_position[i][0] - predict_position[i][0]))
                    DR_distance_avg.append(sum(DR_distance)/len(DR_distance))
                        
                elif scheme == "MAADR":
                    for i in range(100):
                        MAADR_distance.append(abs(real_position[i][0] - predict_position[i][0]))
                    MAADR_distance_avg.append(sum(MAADR_distance)/len(MAADR_distance))
                        
                elif scheme == "Propose":
                    for i in range(100):
                        Propose_distance.append(abs(real_position[i][0] - predict_position[i][0]))
                    Propose_distance_avg.append(sum(Propose_distance)/len(Propose_distance))
                    

    print("===========================")
    print(f"making hit rate png & eps graph")
    
    lag_avg = [41.7, 50.7, 61.1, 71.3, 81.4]
    
    p1 = plt.plot(lag_avg, DR_distance_avg, linestyle = "--", dashes = (4, 4), marker='x', color = colors[2], markerfacecolor = "None", ms = marker_size)
    p2 = plt.plot(lag_avg, MAADR_distance_avg, linestyle = "--", dashes = (5, 5), marker=markers[2], color = "grey", markerfacecolor = "None", ms = marker_size)
    p3 = plt.plot(lag_avg, Propose_distance_avg, linestyle = "--", dashes = (7, 7), marker='*', color = colors[0], markerfacecolor = "None", ms = marker_size)

    # plt.xlabel("Lag Parameter [ms]")
    plt.xlabel("Ltency avg. [ms]")
    plt.ylabel("Mean Euclidean Distance [m]")

    plt.legend((p1[0], p2[0], p3[0]), ("DR", "MAADR", "Proposed"))

    plt.savefig(f"figure/{motion}_shootTime_distance.png", bbox_inches='tight', pad_inches=0)
    plt.savefig(f"figure/{motion}_shootTime_distance.eps", bbox_inches='tight', pad_inches=0)

    plt.clf()
    plt.close()