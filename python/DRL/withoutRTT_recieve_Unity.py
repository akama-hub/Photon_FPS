from __future__ import print_function
import argparse

import numpy as np
from numpy.lib.function_base import diff
import torch
from torch import distributions, nn

from pfrl import agents, explorers, replay_buffers, utils
from pfrl import nn as pnn
from pfrl.q_functions import DistributionalFCStateQFunctionWithDiscreteAction


from argparse import ArgumentParser
from time import sleep
import csv

import logging

import os

import torch.nn.functional as F

import socket
import signal

import math


def main():
    # ctrl-Cがなかなか反応しないのを直す
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    M_SIZE = 1024
    host = '127.0.0.1' 
    # 自分を指定
    serv_port = 50026
    unity_port = 50040
    serv = (host, serv_port)
    unity_addr = (host, unity_port)
    cli_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    cli_sock.bind(serv)
    unity_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)

    delays = [25, 37, 50, 75, 100]

    # delay = delays[0]*2*0.001
    delay = delays[1]*2*0.001
    # delay = delays[2]*2*0.001

    motions = ["ohuku", "curb", "zigzag", "ohukuRandom"]
    motion = motions[0]
    # motion = motions[1]
    # motion = motions[3]

    evaluate_dir = f"../evaluate/{motion}"
    os.makedirs(evaluate_dir, exist_ok=True)

    while True:
        try:
            # start = time.time() #単位は秒

            # unity_sock.sendto("hi".encode("utf-8"), unity_addr)

            cli_data, cli_addr = cli_sock.recvfrom(M_SIZE)
            # clidata = time00000000x00000000y00000000z00000000
            #　負の値を取るとーも一文字になるので注意
            cli_str_data = cli_data.decode("utf-8")
            send_time = ""
            position_x = ""
            position_y = ""
            position_z = ""
            velocity_x = ""
            velocity_y = ""
            velocity_z = ""
            flag = "first"

            Dflag = "first"
            lag = ""
            frame_time = ""

            print("recieving data: ", cli_data)
            for data in cli_str_data:
                if data == "D" and Dflag == "first":
                    Dflag = "delay"
                    print("dalay log")
                    continue
                elif data == "P" and Dflag == "first":
                    Dflag = "predict"
                    print("predict log")
                    continue

                if data == "t" and flag == "first":
                    flag = "time"
                    continue
                elif data == "x":
                    if flag == "time":
                        flag = "position_x"
                    elif flag == "velocity":
                        flag = "velocity_x"
                    continue
                elif data == "y":
                    if flag == "position_x":
                        flag = "position_y"
                    elif flag == "velocity":
                        flag = "velocity_y"
                    continue
                elif data == "z":
                    if flag == "position_y":
                        flag = "position_z"
                    elif flag == "velocity":
                        flag = "velocity_z"
                    continue
                elif data == "v":
                    flag = "velocity"
                    continue
                elif data == "l":
                    flag = "lag"
                    continue
                elif data == "T":
                    flag = "Time"
                    continue

                
                if flag == "time":
                    send_time += data
                if flag == "position_x":
                    position_x += data
                if flag == "position_y":
                    position_y += data
                if flag == "position_z":
                    position_z += data
                if flag == "velocity_x":
                    velocity_x += data
                if flag == "velocity_y":
                    velocity_y += data
                if flag == "velocity_z":
                    velocity_z += data
                if flag == "lag":
                    lag += data
                if flag == "Time":
                    frame_time += data

            if Dflag == "delay":
                # with open(f'{evaluate_dir}/delay_log.csv', 'a') as f:
                # with open(f'{evaluate_dir}/delay_log_lerpumclamped2.csv', 'a') as f:
                # with open(f'{evaluate_dir}/delay_log_interpolate.csv', 'a') as f:
                # with open(f'{evaluate_dir}/delay_log_lerp2.csv', 'a') as f:
                # # with open(f'{evaluate_dir}/delay_log_action.csv', 'a') as f:
                #     writer = csv.writer(f, lineterminator='\n')
                #     writer.writerow([send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z])
                with open(f'{evaluate_dir}/check_lag0.csv', 'a') as f:
                    writer = csv.writer(f, lineterminator='\n')
                    writer.writerow([lag])

            elif Dflag == "predict":
                # with open(f'{evaluate_dir}/predict_log.csv', 'a') as f:
                # with open(f'{evaluate_dir}/predict_log_lerpumclamped2.csv', 'a') as f:
                # with open(f'{evaluate_dir}/predict_log_interpolate3.csv', 'a') as f:
                #     writer = csv.writer(f, lineterminator='\n')
                #     writer.writerow([send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z])
                # with open(f'{evaluate_dir}/predict_log_interpolate.csv', 'a') as f:
                with open(f'{evaluate_dir}/predict_log_lerp2.csv', 'a') as f:
                # with open(f'{evaluate_dir}/predict_log_action.csv', 'a') as f:
                    writer = csv.writer(f, lineterminator='\n')
                    writer.writerow([send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, lag, frame_time])
            
    
        except KeyboardInterrupt:
            print ('\n . . .\n')
            cli_sock.close()
            unity_sock.close()

    

if __name__ == "__main__":
    main()