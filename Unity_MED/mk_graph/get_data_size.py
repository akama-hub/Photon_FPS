import os
import csv

frame_delays = [3, 6, 9]

steps = [-1, -1.5, -2, -2.5, -2.6, -2.7, -2.8, -2.9, -3, -3.1, -3.2, -3.3, -3.4, -3.5, -3.6, -3.7, -3.8, -3.9, -4, -4.1, -4.2, -4.3, -4.4, -4.5, -4.6, -4.7, -4.8, -4.9, -5, -5.1, -5.2, -5.3, -5.4, -5.5, -5.6, -5.7, -5.8, -5.9, -6, -6.1, -6.2, -6.3, -6.4, -6.5, -6.6, -6.7, -6.8, -6.9, -7, -7.1, -7.2, -7.3, -7.4, -7.5, -7.6, -7.7, -7.8, -7.9]
motions = ["ohuku", "curb", "zigzag"]

for motion in motions:
    for frame_delay in frame_delays:
        for step in steps:
            log_dir = f'/mnt/HDD/akama/Unity/CABAC/2mlp/accel/data_size/{motion}/{frame_delay}'
            os.makedirs(log_dir, exist_ok=True)
            change_dir = f'/mnt/HDD/akama/Unity/CABAC/2mlp/accel/{motion}/TP_xyV_xy/{frame_delay}frame_delay/{step}stepsize/change_weights.bin'
            act_dir = f'/mnt/HDD/akama/Unity/CABAC/2mlp/accel/{motion}/TP_xyV_xy/{frame_delay}frame_delay/{step}stepsize/act_weights.bin'

            change_size = os.path.getsize(change_dir)
            act_size = os.path.getsize(act_dir)
            
            print("=======================")
            print("motion: ", motion)
            print("frame_delay: ", frame_delay)
            print("step size: ", step)
            print("change model data size: ", change_size)
            print("act model data size: ", act_size)
            
            with open(f"{log_dir}/data_size.csv", 'a') as f:
                writer = csv.writer(f, lineterminator='\n')
                writer.writerow([step, change_size, act_size])