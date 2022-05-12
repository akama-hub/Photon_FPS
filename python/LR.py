
import argparse

import numpy as np

import csv

import os
from datetime import datetime

import math
from sklearn.linear_model import LinearRegression #LinearRegression
import argparse

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-frame', type=int, help = 'delay(frame) between server and client, 20 ms per frame')
    # args = parser.parse_args()
    
    # frame_delay = args.frame
    for frame_delay in range(1, 11):

        # log_dir = f'/mnt/HDD/akama/Unity/LR-NLR/ohuku/{frame_delay}frame/'
        # log_dir = f'/mnt/HDD/akama/Unity/LR-NLR/ohuku/speed5/{frame_delay}frame/'
        # log_dir = f'/mnt/HDD/akama/Unity/LR-NLR/accel/ohuku/{frame_delay}frame/'
        # log_dir = f'/mnt/HDD/akama/Unity/LR-NLR/accel/curb/{frame_delay}frame/'
        log_dir = f'/mnt/HDD/akama/Unity/LR-NLR/accel/zigzag/{frame_delay}frame/'
        os.makedirs(log_dir, exist_ok=True)

        positions = {}
        velocity = {}

        keys = []

        # with open(f'/mnt/HDD/akama/Unity/mlp/ohuku/ohuku_TPV-6_test.csv') as f:
        # with open(f'/mnt/HDD/akama/Unity/movement_data/ohuku/ohuku.csv') as f:
        # with open(f'/mnt/HDD/akama/Unity/movement_data/ohuku/ohuku_speed_5.csv') as f:
        # with open(f'/mnt/HDD/akama/Unity/movement_data/accel/ohuku/ohuku.csv') as f:
        # with open(f'/mnt/HDD/akama/Unity/movement_data/accel/curb/curb.csv') as f:
        with open(f'/mnt/HDD/akama/Unity/movement_data/accel/zigzag/zigzag.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                row[0] = float(row[0])
                for k in range(1, 7):
                    row[k] = float(row[k])
                positions[row[0]] = [row[1], row[2], row[3]]
                velocity[row[0]] = [row[4], row[5], row[6]]
                # time, x, y, z
                keys.append(float(row[0]))

        last_position_x = np.zeros(4)
        last_position_y = np.zeros(4)
        last_velocity_x = np.zeros(4)
        last_velocity_y = np.zeros(4)
        time = np.zeros(4)

        delay_diff_x = []
        delay_diff_y = []
        delay_diff = []

        LR_diff_x = []
        LR_diff_y = []
        LR_diffs = []

        NLR_diff_x = []
        NLR_diff_y = []
        NLR_diffs = []

        lr = LinearRegression()
        length = len(keys)

        for key in keys:
            if keys.index(key) < 4:
                last_position_x = np.roll(last_position_x, 1)
                last_position_y = np.roll(last_position_y, 1)
                # last_velocity_x = np.roll(last_velocity_x, 1)
                # last_velocity_y = np.roll(last_velocity_y, 1)
                time = np.roll(time, 1)

                time[0] = key
                last_position_x[0] = positions[key][0]
                last_position_y[0] = positions[key][2]
                # last_velocity_x[0] = velocity[key][0]
                # last_velocity_y[0] = velocity[key][2]
                # last_position_x = positions[key][0]
                # last_position_y = positions[key][1]
                # last_velocity_x = velocity[key][0]
                # last_velocity_y = velocity[key][1]

                continue
            
            index = keys.index(key) #最新の位置情報を持ってるときのインデックス

            if index + 1 >= length - frame_delay:
                break

            T = time.reshape(-1,1)
            X = last_position_x.reshape(-1,1)
            Y = last_position_y.reshape(-1,1)

            lr.fit(T, X)
            LR_predict_x = lr.coef_[0] * (time[0] + frame_delay * (time[0] - time[1])) + lr.intercept_
            lr.fit(T, Y)
            LR_predict_y = lr.coef_[0] * (time[0] + frame_delay * (time[0] - time[1])) + lr.intercept_

            T = T.squeeze()
            X = X.squeeze()
            Y = Y.squeeze()

            NLR_predict_x = np.poly1d(np.polyfit(T, X, 2))(time[0] + frame_delay * (time[0] - time[1]))
            NLR_predict_y = np.poly1d(np.polyfit(T, Y, 2))(time[0] + frame_delay * (time[0] - time[1]))

            delay_x = abs(positions[keys[index + frame_delay-1]][0]-last_position_x[0])
            delay_y = abs(positions[keys[index + frame_delay-1]][2]-last_position_y[0])
            diff = math.sqrt(delay_x ** 2 + delay_y ** 2)

            LR_x = abs(positions[keys[index + frame_delay-1]][0] - LR_predict_x)
            LR_y = abs(positions[keys[index + frame_delay-1]][2] - LR_predict_y)
            LR_diff = math.sqrt(LR_x ** 2 + LR_y ** 2)

            NLR_x = abs(positions[keys[index + frame_delay-1]][0] - NLR_predict_x)
            NLR_y = abs(positions[keys[index + frame_delay-1]][2] - NLR_predict_y)
            NLR_diff = math.sqrt(NLR_x ** 2 + NLR_y ** 2)

            delay_diff_x.append(delay_x)
            delay_diff_y.append(delay_y)
            delay_diff.append(diff)

            LR_diff_x.append(LR_x)
            LR_diff_y.append(LR_y)
            LR_diffs.append(LR_diff)

            NLR_diff_x.append(NLR_x)
            NLR_diff_y.append(NLR_y)
            NLR_diffs.append(NLR_diff)

            last_position_x = np.roll(last_position_x, 1)
            last_position_y = np.roll(last_position_y, 1)
            # last_velocity_x = np.roll(last_velocity_x, 1)
            # last_velocity_y = np.roll(last_velocity_y, 1)
            time = np.roll(time, 1)

            last_position_x[0] = positions[key][0]
            last_position_y[0] = positions[key][2]
            # last_velocity_x[0] = velocity[key][0]
            # last_velocity_y[0] = velocity[key][2]
            time[0] = key

            # with open(f'{log_dir}/check.csv', 'a') as f:
            #     writer = csv.writer(f, lineterminator='\n')
            #     writer.writerow([delay_x, delay_y, diff, LR_x, LR_y, LR_diff, NLR_x, NLR_y, NLR_diff])

        average_diff_x = sum(delay_diff_x)/len(delay_diff_x)
        average_diff_y = sum(delay_diff_y)/len(delay_diff_y)
        average_diff = sum(delay_diff)/len(delay_diff)

        average_LR_diff_x = sum(LR_diff_x)/len(LR_diff_x)
        average_LR_diff_y = sum(LR_diff_y)/len(LR_diff_y)
        average_LR_diff = sum(LR_diffs)/len(LR_diffs)

        average_NLR_diff_x = sum(NLR_diff_x)/len(NLR_diff_x)
        average_NLR_diff_y = sum(NLR_diff_y)/len(NLR_diff_y)
        average_NLR_diff = sum(NLR_diffs)/len(NLR_diffs)

        print("NC: ", average_diff_x, average_diff_y, average_diff)
        print("LR: ", average_LR_diff_x, average_LR_diff_y, average_LR_diff)
        print("NLR: ", average_NLR_diff_x, average_NLR_diff_y, average_NLR_diff)

        with open(f'{log_dir}/result.csv', 'a') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow([frame_delay, average_diff_x, average_diff_y, average_diff, average_LR_diff_x, average_LR_diff_y, average_LR_diff, average_NLR_diff_x, average_NLR_diff_y, average_NLR_diff])

    
if __name__ == "__main__":
    main()