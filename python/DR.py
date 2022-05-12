
import argparse

import numpy as np

import csv

import os
from datetime import datetime

import math
import argparse

import numpy as np

def DR(position, velocity, delay):
    predict_x = position[0] + velocity[0] * delay
    predict_y = position[1] + velocity[1] * delay
    return predict_x, predict_y

def MAADR(position, velocity, accelelation, last_accelelation, delay):
    predict_x = 0
    predict_y = 0

    if accelelation[0] == 0 and accelelation[1] == 0:
        predict_x = position[0] + velocity[0] * delay
        predict_y = position[1] + velocity[1] * delay
    elif accelelation[0] == last_accelelation[0] and accelelation[1] == last_accelelation[1]:
        predict_x = position[0] + velocity[0] * delay + accelelation[0] * (delay ** 2) / 2
        predict_y = position[1] + velocity[1] * delay + accelelation[1] * (delay ** 2) / 2
    else:
        np_velocity = np.array(velocity)
        np_accelelation = np.array(accelelation)
        k = np.linalg.norm(np.cross(np_velocity, np_accelelation)) / (np.linalg.norm(np_velocity)**3)
        if k == 0:
            predict_x = position[0] + velocity[0] * delay + accelelation[0] * (delay ** 2) / 2
            predict_y = position[1] + velocity[1] * delay + accelelation[1] * (delay ** 2) / 2
        else:
            accelelation_x = k * (np.linalg.norm(np_velocity) ** 2) * (np_velocity[0] / np.linalg.norm(np_velocity))
            accelelation_y = k * (np.linalg.norm(np_velocity) ** 2) * (np_velocity[1] / np.linalg.norm(np_velocity))

            predict_x = position[0] + velocity[0] * delay + accelelation_x * (delay ** 2) / 2
            predict_y = position[1] + velocity[1] * delay + accelelation_y * (delay ** 2) / 2

    return predict_x, predict_y

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-frame', type=int, help = 'delay(frame) between server and client, 20 ms per frame')
    # args = parser.parse_args()
    
    motion = "ohuku"
    # motion = "curb"
    # motion = "zigzag"
    
    method = ["DR", "MAADR"]

    for frame_delay in range(1, 11):
        DR_diff_x = []
        DR_diff_y = []
        DR_diffs = []

        MAADR_diff_x = []
        MAADR_diff_y = []
        MAADR_diffs = []

        for meth in method:
            log_dir = f'/mnt/HDD/akama/Unity/DR-MAADR/{motion}/'
            os.makedirs(log_dir, exist_ok=True)

            positions = {}
            velocity = {}

            keys = []

            
            if motion == "ohuku":
                movement_file = '/mnt/HDD/akama/Unity/movement_data/accel/ohuku/ohuku.csv'
            elif motion == "curb":
                movement_file = '/mnt/HDD/akama/Unity/movement_data/accel/curb/curb.csv'
            elif motion == "zigzag":
                movement_file = '/mnt/HDD/akama/Unity/movement_data/accel/zigzag/zigzag.csv'

            with open(movement_file) as f:
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
            last_accelelation_x = np.zeros(4)
            last_accelelation_y = np.zeros(4)
            time = np.zeros(4)

            delay_diff_x = []
            delay_diff_y = []
            delay_diff = []

            length = len(keys)
            delay = frame_delay * 0.02

            for key in keys:
                if keys.index(key) < 4:
                    last_position_x = np.roll(last_position_x, 1)
                    last_position_y = np.roll(last_position_y, 1)
                    last_velocity_x = np.roll(last_velocity_x, 1)
                    last_velocity_y = np.roll(last_velocity_y, 1)
                    last_accelelation_x = np.roll(last_accelelation_x, 1)
                    last_accelelation_y = np.roll(last_accelelation_y, 1)

                    time = np.roll(time, 1)

                    time[0] = key
                    last_position_x[0] = positions[key][0]
                    last_position_y[0] = positions[key][2]
                    last_velocity_x[0] = velocity[key][0]
                    last_velocity_y[0] = velocity[key][2]
                    last_accelelation_x[0] = last_velocity_x[0] - last_velocity_x[1]
                    last_accelelation_y[0] = last_velocity_y[0] - last_velocity_y[1]
                    continue
                
                index = keys.index(key) #最新の位置情報を持ってるときのインデックス

                if index + 1 >= length - frame_delay:
                    break

                position = [last_position_x[0], last_position_y[0]]
                vel = [last_velocity_x[0], last_velocity_y[0]]
                accelelation = [last_accelelation_x[0], last_accelelation_y[0]]
                past_accelelation = [last_accelelation_x[1], last_accelelation_y[1]]

                delay_x = abs(positions[keys[index + frame_delay-1]][0]-last_position_x[0])
                delay_y = abs(positions[keys[index + frame_delay-1]][2]-last_position_y[0])
                diff = math.sqrt(delay_x ** 2 + delay_y ** 2)

                delay_diff_x.append(delay_x)
                delay_diff_y.append(delay_y)
                delay_diff.append(diff)

                if meth == "DR":
                    DR_predict_x, DR_predict_y = DR(position, vel, delay)

                    DR_x = abs(positions[keys[index + frame_delay-1]][0] - DR_predict_x)
                    DR_y = abs(positions[keys[index + frame_delay-1]][2] - DR_predict_y)
                    DR_diff = math.sqrt(DR_x ** 2 + DR_y ** 2)

                    DR_diff_x.append(DR_x)
                    DR_diff_y.append(DR_y)
                    DR_diffs.append(DR_diff)

                elif meth == "MAADR":
                    MAADR_predict_x, MAADR_predict_y = MAADR(position, vel, accelelation, past_accelelation, delay)

                    MAADR_x = abs(positions[keys[index + frame_delay-1]][0] - MAADR_predict_x)
                    MAADR_y = abs(positions[keys[index + frame_delay-1]][2] - MAADR_predict_y)
                    MAADR_diff = math.sqrt(MAADR_x ** 2 + MAADR_y ** 2)

                    MAADR_diff_x.append(MAADR_x)
                    MAADR_diff_y.append(MAADR_y)
                    MAADR_diffs.append(MAADR_diff)

                last_position_x = np.roll(last_position_x, 1)
                last_position_y = np.roll(last_position_y, 1)
                last_velocity_x = np.roll(last_velocity_x, 1)
                last_velocity_y = np.roll(last_velocity_y, 1)
                last_accelelation_x = np.roll(last_accelelation_x, 1)
                last_accelelation_y = np.roll(last_accelelation_y, 1)
                time = np.roll(time, 1)

                last_position_x[0] = positions[key][0]
                last_position_y[0] = positions[key][2]
                last_velocity_x[0] = velocity[key][0]
                last_velocity_y[0] = velocity[key][2]
                last_accelelation_x[0] = last_velocity_x[0] - last_velocity_x[1]
                last_accelelation_y[0] = last_velocity_y[0] - last_velocity_y[1]
                time[0] = key

            # print("======================================================")
            # print(meth, " method: frame ", frame_delay, " delay finished")
            # average_diff_x = sum(delay_diff_x)/len(delay_diff_x)
            # average_diff_y = sum(delay_diff_y)/len(delay_diff_y)
            # average_diff = sum(delay_diff)/len(delay_diff)

            # print("NC: ", average_diff_x, average_diff_y, average_diff)
            
            if meth == "DR":
                print("======================================================")
                print(meth, " method: frame ", frame_delay, " delay finished")
                average_diff_x = sum(delay_diff_x)/len(delay_diff_x)
                average_diff_y = sum(delay_diff_y)/len(delay_diff_y)
                average_diff = sum(delay_diff)/len(delay_diff)

                print("NC: ", average_diff_x, average_diff_y, average_diff)

                average_DR_diff_x = sum(DR_diff_x)/len(DR_diff_x)
                average_DR_diff_y = sum(DR_diff_y)/len(DR_diff_y)
                average_DR_diff = sum(DR_diffs)/len(DR_diffs)

                print("DR: ", average_DR_diff_x, average_DR_diff_y, average_DR_diff)

            elif meth == "MAADR":
                average_MAADR_diff_x = sum(MAADR_diff_x)/len(MAADR_diff_x)
                average_MAADR_diff_y = sum(MAADR_diff_y)/len(MAADR_diff_y)
                average_MAADR_diff = sum(MAADR_diffs)/len(MAADR_diffs)
        
                print("MAADR: ", average_MAADR_diff_x, average_MAADR_diff_y, average_MAADR_diff)

        with open(f'{log_dir}/result.csv', 'a') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow([frame_delay, average_diff_x, average_diff_y, average_diff, average_DR_diff_x, average_DR_diff_y, average_DR_diff, average_MAADR_diff_x, average_MAADR_diff_y, average_MAADR_diff])

    
if __name__ == "__main__":
    main()