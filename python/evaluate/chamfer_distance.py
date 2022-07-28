import numpy as np
import matplotlib.pyplot as plt
import csv
import math

def get_chamfer_distance(key, keys, index, position1, position2):
    while True:
        if key > keys[index]:
            index += 1
        elif key == keys[index]:
            diff_x = abs(position1[key][0] - position2[keys[index]][0])
            diff_y = abs(position1[key][1] - position2[keys[index]][1])
            diff_z = abs(position1[key][2] - position2[keys[index]][2])

            diff = math.sqrt(diff_x**2 + diff_y**2 + diff_z**2)
            return index, diff
        else:
            if key - keys[index] <= key - keys[index-1]:
                diff_x = abs(position1[key][0] - position2[keys[index]][0])
                diff_y = abs(position1[key][1] - position2[keys[index]][1])
                diff_z = abs(position1[key][2] - position2[keys[index]][2])

                diff = math.sqrt(diff_x**2 + diff_y**2 + diff_z**2)
                return index, diff
            else:
                diff_x = abs(position1[key][0] - position2[keys[index-1]][0])
                diff_y = abs(position1[key][1] - position2[keys[index-1]][1])
                diff_z = abs(position1[key][2] - position2[keys[index-1]][2])

                diff = math.sqrt(diff_x**2 + diff_y**2 + diff_z**2)
                return index-1, diff
    
def main():
    plt.rcParams["font.size"] = 20
    # plt.rcParams["legend.labelspacing"] = 0
    plt.rcParams["font.family"] = 'Times New Roman'
    plt.figure(figsize = (8.0, 6.0))
    markers = ["o", "v", "s", ">", "<"]
    colors = ["r", "b", "g", "c", "m", "y", "k"]

    marker_size = 12

    # motion = "ohuku"
    # motion = "curb"
    # motion = "zigzag"

    motions = ["ohuku", "curb", "zigzag"]
    # motion = motions[0]
    motion = motions[1]

    # methods = ["NC", "DR", "MAADR", "Proposed"]
    # methods = ["Proposed_rcv_delayed"]
    methods = ["DR", "MAADR", "DRL_distance"]

    delays = [0, 20, 40]

    NC_diff = np.array([])
    DR_diff = np.array([])
    MAADR_diff = np.array([])
    Proposed_diff = np.array([])

    for method in methods:
        for delay in delays:
            # real_log_file = f'EvaluateDiffLog/Lag{delay}/{motion}/{method}/Real_log.csv'
            real_log_file = f'chamfer/Fixed30FPS_SendRate60_RTT/Lag{delay}/{motion}/{method}/Real_log.csv'
            # delay_log_file = f'EvaluateDiffLog/Lag{delay}/{motion}/{method}/delayed_log.csv'
            if method == "DR" or method == "MAADR":
                estimate_file = f'chamfer/Fixed30FPS_SendRate60_RTT/Lag{delay}/{motion}/{method}/Delayed_log.csv'
            elif method == "DRL_distance":
                estimate_file = f'chamfer/Fixed30FPS_SendRate60_RTT/Lag{delay}/{motion}/{method}/Predict_log.csv'
            
            real_key = []
            real_position = {}

            with open(real_log_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    for i in range(4):
                        row[i] = float(row[i])
                        
                    real_key.append(row[0])
                    real_position[row[0]] = [row[1], row[2], row[3]]

            # delay_key = []
            # delay_position = {}

            # with open(delay_log_file) as f:
            #     reader = csv.reader(f)
            #     for row in reader:
            #         for i in range(4):
            #             row[i] = float(row[i])

            #         delay_key.append(row[0])
            #         delay_position[row[0]] = [row[1], row[2], row[3]]

            estimate_key = []
            estimate_position = {}

            with open(estimate_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[0] == "P":
                        for i in range(1,5):
                            row[i] = float(row[i])

                            estimate_key.append(row[1])
                            estimate_position[row[1]] = [row[2], row[3], row[4]]
                    else:   
                        for i in range(4):
                            row[i] = float(row[i])

                        estimate_key.append(row[0])
                        estimate_position[row[0]] = [row[1], row[2], row[3]]


            # delay_index = 0
            real_index = 0
            estimate_index = 0

            diff = 0
            # delay_diff = 0
            estimate_diff = 0

            # delay_length = len(delay_key)
            real_length = len(real_key)
            estimate_length = len(estimate_key)

            delay_count = 0
            estimate_count = 0

            for key in real_key:
                if real_key.index(key) <= 10:
                    continue
                elif real_length - real_key.index(key) <= 10:
                    break
                else:
                    # if delay_length - delay_index > 10:
                    #     delay_index, diff = get_chamfer_distance(key, delay_key, delay_index, real_position, delay_position)
                    #     delay_diff += diff
                    #     delay_count += 1
                    
                    if estimate_length - estimate_index > 10:
                        estimate_index, diff = get_chamfer_distance(key, estimate_key, estimate_index, real_position, estimate_position)
                        estimate_diff += diff
                        estimate_count += 1

            # for key in delay_key:
            #     if delay_key.index(key) <= 10:
            #         continue
            #     elif delay_length - delay_key.index(key) <= 10:
            #         break
            #     else:
            #         if real_length - real_index > 10:
            #             real_index, diff = get_chamfer_distance(key, real_key, real_index, delay_position, real_position)
            #             delay_diff += diff
            #             delay_count += 1

            real_index = 0

            for key in estimate_key:
                if estimate_key.index(key) <= 10:
                    continue
                elif estimate_length - estimate_key.index(key) <= 10:
                    break
                else:
                    if real_length - real_index > 10:
                        real_index, diff = get_chamfer_distance(key, real_key, real_index, estimate_position, real_position)
                        estimate_diff += diff
                        estimate_count += 1

            # delay_diff_avg = delay_diff / delay_count
            estimate_diff_avg = estimate_diff / estimate_count

            print("===========================")
            print("Delay: ", delay)

            # print("delay_diff: ", delay_diff_avg)
            print(method, ": ", estimate_diff_avg)

            if method == "NC":
                NC_diff = np.append(NC_diff, estimate_diff_avg)
            elif method == "DR":
                DR_diff = np.append(DR_diff, estimate_diff_avg)
            elif method == "MAADR":
                MAADR_diff = np.append(MAADR_diff, estimate_diff_avg)
            # elif method == "Proposed":
            elif method == "DRL_distance":
                Proposed_diff = np.append(Proposed_diff, estimate_diff_avg)
            
            print("===========================")

    print("!!!===========================!!!")
    print(f"making diff position png & eps graph")

    # p1 = plt.plot(delays, NC_diff, linestyle = "--", dashes = (1, 1), marker=markers[0], color = colors[6], markerfacecolor = "None", ms = marker_size)
    p2 = plt.plot(delays, DR_diff, linestyle = "--", dashes = (4, 4), marker='x', color = colors[2], markerfacecolor = "None", ms = marker_size)
    p3 = plt.plot(delays, MAADR_diff, linestyle = "--", dashes = (5, 5), marker=markers[2], color = "grey", markerfacecolor = "None", ms = marker_size)
    p4 = plt.plot(delays, Proposed_diff, linestyle = "--", dashes = (7, 7), marker='*', color = colors[0], markerfacecolor = "None", ms = marker_size)
    
    # plt.xlabel("delay[F] (33 ms/frame)")
    plt.xlabel("Delay [ms]")
    plt.ylabel("Chamfer Distance [m]")

    # plt.legend((p1[0], p2[0], p3[0], p4[0]), ("NC", "DR [6]", "MAADR [7]", "Proposed"), loc = 2)
    plt.legend((p2[0], p3[0], p4[0]), ("DR [6]", "MAADR [7]", "Proposed"), loc = 2)
    
    # plt.savefig(f"Figure/CCNC_{motion}.eps", bbox_inches='tight', pad_inches=0)
    plt.savefig(f"Figure/MMM_{motion}.png", bbox_inches='tight', pad_inches=0)

    plt.clf()
    plt.close()
    print("!!!===========================!!!")
            

if __name__ == "__main__":
    main()
