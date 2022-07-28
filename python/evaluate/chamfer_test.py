import numpy as np
import csv
import math

from sklearn.metrics import euclidean_distances

def get_chamfer_distance(key, keys, index, position1, position2):
    a = 0
    while True:
        if key > keys[index]:
            index += 1
        elif key == keys[index]:
            diff_x = abs(position1[key][0] - position2[keys[index]][0])
            diff_y = abs(position1[key][1] - position2[keys[index]][1])
            diff_z = abs(position1[key][2] - position2[keys[index]][2])

            diff = math.sqrt(diff_x**2 + diff_y**2 + diff_z**2)
            a=1
            # print("predict: ", position1[key][0])
            # print("Real: ", position2[key][0])
            return index, diff, a
        else:
            if key - keys[index] <= key - keys[index-1]:
                diff_x = abs(position1[key][0] - position2[keys[index]][0])
                diff_y = abs(position1[key][1] - position2[keys[index]][1])
                diff_z = abs(position1[key][2] - position2[keys[index]][2])

                diff = math.sqrt(diff_x**2 + diff_y**2 + diff_z**2)
                return index, diff, a
            else:
                diff_x = abs(position1[key][0] - position2[keys[index-1]][0])
                diff_y = abs(position1[key][1] - position2[keys[index-1]][1])
                diff_z = abs(position1[key][2] - position2[keys[index-1]][2])

                diff = math.sqrt(diff_x**2 + diff_y**2 + diff_z**2)
                return index-1, diff, a

def main():
    motions = ["ohuku", "curb", "zigzag"]
    motion = motions[0]

    # methods = ["NC", "DR", "MAADR", "Proposed"]
    # methods = ["Proposed_rcv_delayed"]
    methods = ["DR", "MAADR"]

    delays = [0, 20, 40]

    diff = np.array([])


    for method in methods:
        for delay in delays:
            # real_log_file = f'chamfer/Fixed30FPS/Lag{delay}/{motion}/{method}/Real_log.csv'
            # delay_log_file = f'chamfer/Fixed30FPS/Lag{delay}/{motion}/{method}/Delayed_log.csv'
            # estimate_file = f'EvaluateDiffLog/Lag{delay}/{motion}/{method}/predict_log.csv'

            real_log_file = f'chamfer/Fixed30FPS_SendRate60_RTT/Lag{delay}/{motion}/{method}/Real_log.csv'
            delay_log_file = f'chamfer/Fixed30FPS_SendRate60_RTT/Lag{delay}/{motion}/{method}/Delayed_log.csv'
            
            real_key = []
            real_position = {}

            with open(real_log_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    for i in range(4):
                        row[i] = float(row[i])
                        
                    real_key.append(row[0])
                    real_position[row[0]] = [row[1], row[2], row[3]]

            delay_key = []
            delay_position = {}

            with open(delay_log_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    for i in range(4):
                        row[i] = float(row[i])

                    delay_key.append(row[0])
                    delay_position[row[0]] = [row[1], row[2], row[3]]

            # estimate_key = []
            # estimate_position = {}

            # with open(estimate_file) as f:
            #     reader = csv.reader(f)
            #     for row in reader:
            #         for i in range(4):
            #             row[i] = float(row[i])

            #         estimate_key.append(row[0])
            #         estimate_position[row[0]] = [row[1], row[2], row[3]]


            delay_index = 0
            real_index = 0
            # estimate_index = 0

            diff = 0
            delay_diff = 0
            # estimate_diff = 0

            delay_length = len(delay_key)
            real_length = len(real_key)
            # estimate_length = len(estimate_key)

            delay_count = 0
            # estimate_count = 0

            flag = 0
            euclid_dis = 0
            euclid_count = 0

            for key in real_key:
                if real_key.index(key) <= 10:
                    continue
                elif real_length - real_key.index(key) <= 10:
                    break
                else:
                    if delay_length - delay_index > 10:
                        delay_index, diff, flag = get_chamfer_distance(key, delay_key, delay_index, real_position, delay_position)
                        if flag == 1:
                            euclid_dis += diff
                            euclid_count += 1
                        delay_diff += diff
                        delay_count += 1
                    
                    # if estimate_length - estimate_index > 10:
                    #     estimate_index, diff = get_chamfer_distance(key, estimate_key, estimate_index, real_position, estimate_position)
                    #     estimate_diff += diff
                    #     estimate_count += 1

            for key in delay_key:
                if delay_key.index(key) <= 10:
                    continue
                elif delay_length - delay_key.index(key) <= 10:
                    break
                else:
                    if real_length - real_index > 10:
                        real_index, diff, flag = get_chamfer_distance(key, real_key, real_index, delay_position, real_position)
                        delay_diff += diff
                        delay_count += 1

            real_index = 0

            # for key in estimate_key:
            #     if estimate_key.index(key) <= 10:
            #         continue
            #     elif estimate_length - estimate_key.index(key) <= 10:
            #         break
            #     else:
            #         if real_length - real_index > 10:
            #             real_index, diff = get_chamfer_distance(key, real_key, real_index, estimate_position, real_position)
            #             estimate_diff += diff
            #             estimate_count += 1

            delay_diff_avg = delay_diff / delay_count
            # estimate_diff_avg = estimate_diff / estimate_count
            if euclid_count != 0:
                euclid_avg = euclid_dis / euclid_count
            else:
                euclid_avg = 0

            print("===========================")
            print("Delay: ", delay)

            print("delay_diff: ", delay_diff_avg)
            print("count: ", delay_count)
            print("euclid distance: ", euclid_avg)
            print("count: ", euclid_count)
            # print(method, ": ", estimate_diff_avg)

            # if method == "NC":
            #     NC_diff = np.append(NC_diff, estimate_diff_avg)
            # elif method == "DR":
            #     DR_diff = np.append(DR_diff, estimate_diff_avg)
            # elif method == "MAADR":
            #     MAADR_diff = np.append(MAADR_diff, estimate_diff_avg)
            # elif method == "Proposed":
            #     Proposed_diff = np.append(Proposed_diff, estimate_diff_avg)
            
            print("===========================")

    print("!!!===========================!!!")
    print(f"making diff position png & eps graph")

            

if __name__ == "__main__":
    main()
