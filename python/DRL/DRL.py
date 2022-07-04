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

linear_speed = 0.02
nonlinear_speed = linear_speed * math.sqrt(2) / 2
#0.014142

max_linear_speed = 0.1
max_nonlinear_speed = max_linear_speed * math.sqrt(2) / 2
#0.1697

def linear_move(time, speed, move_direction):
    move = 0
    if move_direction > 0:
        if speed <= 0:
            speed = linear_speed

        elif speed > max_linear_speed:
            speed = max_linear_speed

        for _ in range(time):
            move += speed
            speed += linear_speed
            if speed > max_linear_speed:
                speed = max_linear_speed
            
    elif move_direction < 0:
        if speed >= 0:
            speed = -linear_speed
            
        elif speed < -max_linear_speed:
            speed = -max_linear_speed
        for _ in range(time):
            move += speed
            speed -= linear_speed
            if speed < -max_linear_speed:
                speed = -max_linear_speed
            
    else:
        move = 0

    # print("move: ", move)
    return move

def linear_velocity(time, speed, move_direction):
    if move_direction > 0:
        if speed <= 0:
            speed = linear_speed
            time -= 1
        for _ in range(time):
            speed += linear_speed
        if speed > max_linear_speed:
            speed = max_linear_speed
            
    elif move_direction < 0:
        if speed >= 0:
            speed = -linear_speed
            time -= 1
        for _ in range(time):
            speed -= linear_speed
        if speed < -max_linear_speed:
            speed = -max_linear_speed
            
    else:
        speed = 0

    # print("velocity: ", speed)
    return speed

def nonlinear_move(time, speed, move_direction):
    move = 0
    if move_direction > 0:
        if speed <= 0:
            speed = nonlinear_speed
            
        elif speed > max_nonlinear_speed:
            speed = max_nonlinear_speed

        for _ in range(time):
            move += speed
            speed += nonlinear_speed
            if speed > max_nonlinear_speed:
                speed = max_nonlinear_speed
            
    elif move_direction < 0:
        if speed >= 0:
            speed = -nonlinear_speed
            
        elif speed < -max_nonlinear_speed:
            speed = -max_nonlinear_speed
        for _ in range(time):
            move += speed
            speed -= nonlinear_speed
            if speed < -max_nonlinear_speed:
                speed = -max_nonlinear_speed
            
    else:
        move = 0

    # print("move: ", move)
    return move

def nonlinear_velocity(time, speed, move_direction):
    if move_direction > 0:
        if speed < 0:
            speed = nonlinear_speed
            time -= 1
        for _ in range(time):
            speed += nonlinear_speed
        if speed > max_nonlinear_speed:
            speed = max_nonlinear_speed
            
    elif move_direction < 0:
        if speed >= 0:
            speed = -nonlinear_speed
            time -= 1
        for _ in range(time):
            speed -= nonlinear_speed
        if speed < -max_nonlinear_speed:
            speed = -max_nonlinear_speed
            
    else:
        speed = 0

    # print("velocity: ", speed)
    return speed


def calculateLine(x1, x2, t1, t2):
    if t1 - t2 == 0:
        a = 0
        b = 0
    else:
        a = (x1 - x2) / (t1 - t2)
        b = x1 - a * t1
    return a, b

def main():
    # ctrl-Cがなかなか反応しないのを直す
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    M_SIZE = 1024
    host = '127.0.0.1' 
    # 自分を指定
    serv_port = 50020
    unity_port = 50021
    serv = (host, serv_port)
    unity_addr = (host, unity_port)
    cli_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    cli_sock.bind(serv)
    unity_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)

    pos_x = np.zeros(4)
    pos_y = np.zeros(4)
    vel_x = np.zeros(4)
    vel_y = np.zeros(4)
    t = np.zeros(4)

    frame_delay = 1

    parser = ArgumentParser()
    parser.add_argument("-m", "--motion", type=str)
    parser.add_argument("-l", "--latency", type=int)
    # parser.add_argument("-change_model", type=int)
    # parser.add_argument("-act_model", type=int)

    args = parser.parse_args()

    # ubuntu garellia
    if args.motion == "ohuku":
        model = "20220611-13:52:07"
        model_num = 2201
    elif args.motion == "curb":
        model = "Cpu_0613_2047.csv"
        model_num = 9701
    elif args.motion == "ohukuRandom":
        model = "20220611-13:50:55"
        model_num = 3301
    elif args.motion == "zigzag":
        model = "20220623-13:17:15"
        model_num = 9901

    model_dir =f'../../DRLModels/{args.motion}/{model}'

    evaluate_dir = f"../evaluate/EvaluateDiffLog/Lag{args.latency}/{args.motion}/Proposed"
    os.makedirs(evaluate_dir, exist_ok=True)

    # home pc
    # model_dir =f'../../DRLModels/{motion}/'

    logging.basicConfig(level=20)

    # Set a random seed used in PFRL.
    utils.set_random_seed(0)

    n_dim_obs = 20
    n_actions = 9
    n_frames = 10
    n_atoms = 51
    v_max = 10
    v_min = -10
    n_hidden_channels = 100
    n_hidden_layers = 3
    nonlinearity = F.relu
    last_wscale = 1.0
    
    change_q_func = DistributionalFCStateQFunctionWithDiscreteAction(n_dim_obs, n_frames, n_atoms, v_min, v_max, n_hidden_channels, n_hidden_layers, nonlinearity, last_wscale)
    act_q_func = DistributionalFCStateQFunctionWithDiscreteAction(n_dim_obs, n_actions, n_atoms, v_min, v_max, n_hidden_channels, n_hidden_layers, nonlinearity, last_wscale)
    """Distributional fully-connected Q-function with discrete actions.
    Args:
        n_dim_obs (int): Number of dimensions of observation space.
        n_actions (int): Number of actions in action space.
        n_atoms (int): Number of atoms of return distribution.
        v_min (float): Minimum value this model can approximate.
        v_max (float): Maximum value this model can approximate.
        n_hidden_channels (int): Number of hidden channels.
        n_hidden_layers (int): Number of hidden layers.
        nonlinearity (callable): Nonlinearity applied after each hidden layer.
        last_wscale (float): Weight scale of the last layer.
    """

    # Noisy nets
    pnn.to_factorized_noisy(change_q_func, sigma_scale=0.5)
    pnn.to_factorized_noisy(act_q_func, sigma_scale=0.5)
    # Turn off explorer
    explorer = explorers.Greedy()

    change_opt = torch.optim.Adam(change_q_func.parameters(), 6.25e-5, eps=1.5 * 10 ** -4)
    act_opt = torch.optim.Adam(act_q_func.parameters(), 6.25e-5, eps=1.5 * 10 ** -4)

    # 学習用データ保存領域のサイズ
    capacity = 10**5
    betasteps = capacity - 1000 // 4

    change_rbuf = replay_buffers.PrioritizedReplayBuffer(
        capacity,
        alpha=0.5,
        beta0=0.4,
        betasteps=betasteps,
        num_steps=3,
        normalize_by_max="memory",
    )

    act_rbuf = replay_buffers.PrioritizedReplayBuffer(
        capacity,
        alpha=0.5,
        beta0=0.4,
        betasteps=betasteps,
        num_steps=3,
        normalize_by_max="memory",
    )

    def phi(x):
        # Feature extractor
        return np.asarray(x, dtype=np.float32) / 255

    change_agent = agents.CategoricalDoubleDQN(
        change_q_func,
        change_opt,
        change_rbuf,
        gpu=0,
        gamma=0.99,
        explorer=explorer,
        minibatch_size=32,
        replay_start_size=2 * 10 ** 4,
        target_update_interval=32000,
        update_interval=4,
        batch_accumulator="mean",
        phi=phi,
    )
    change_agent.load(f'{model_dir}/change_model{model_num}')

    act_agent = agents.CategoricalDoubleDQN(
        act_q_func,
        act_opt,
        act_rbuf,
        gpu=0,
        gamma=0.99,
        explorer=explorer,
        minibatch_size=32,
        replay_start_size=2 * 10 ** 4,
        target_update_interval=32000,
        update_interval=4,
        batch_accumulator="mean",
        phi=phi,
    )
    act_agent.load(f'{model_dir}/act_model{model_num}')

    n_input = 20

    obs = np.zeros(n_input, dtype=np.float32)
    last_action = 0

    cnt = 0

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
            
            print(send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z)
            # position_x = "00000020"

            if Dflag == "delay":
            
                if cnt < 4:
                    pos_x[0] = float(position_x)
                    pos_y[0] = float(position_z)
                    vel_x[0] = float(velocity_x)
                    vel_y[0] = float(velocity_z)
                    t[0] = float(send_time)

                    cnt += 1

                else:
                    pos_x = np.roll(pos_x, 1)
                    pos_y = np.roll(pos_y, 1)
                    vel_x = np.roll(vel_x, 1)
                    vel_y = np.roll(vel_y, 1)
                    t = np.roll(t, 1)

                    pos_x[0] = float(position_x)
                    pos_y[0] = float(position_z)
                    vel_x[0] = float(velocity_x)
                    vel_y[0] = float(velocity_z)
                    t[0] = float(send_time)

                    obs = [t[0], pos_x[0], pos_y[0], vel_x[0], vel_y[0], t[1], pos_x[1], pos_y[1], vel_x[1], vel_y[1], t[2], pos_x[2], pos_y[2], vel_x[2], vel_y[2], t[3], pos_x[3], pos_y[3], vel_x[3], vel_y[3]]
                    
                    action = act_agent.act(obs)
                    n_frames_change = change_agent.act(obs)
                    
                    ##########################
                    fps = t[0] - t[1]
                    if fps != 0:
                        frame_delay = round(lag / fps)
                    else:
                        pass

                    if n_frames_change > frame_delay:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = pos_x[1] + linear_move(frame_delay, vel_x[1] * linear_speed, vel_x[1])
                            predict_y = pos_y[1] + linear_move(frame_delay, vel_y[1] * linear_speed, vel_y[1])
                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                            predict_x = pos_x[1] + nonlinear_move(frame_delay, vel_x[1] * linear_speed, vel_x[1])
                            predict_y = pos_y[1] + nonlinear_move(frame_delay, vel_y[1] * linear_speed, vel_y[1])
                        else:
                            predict_x = pos_x[1]
                            predict_y = pos_y[1]

                    else:
                        if action == 0:
                            if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                                predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1])

                                predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])
                            elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                                predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1])
                                
                                predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])
                            else:
                                predict_x = pos_x[1]
                                predict_y = pos_y[1]

                        elif action == 1:
                            if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                                predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), 1)
                                
                                predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])

                            elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8:  
                                predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), 1) , 1)
                                
                                predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])

                            else:
                                predict_x = pos_x[1] + linear_move(frame_delay - n_frames_change , 0, 1)
                                predict_y = pos_y[1]

                        elif action == 2:
                            if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                                predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), -1)
                                
                                predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])
                            
                            elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                                predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), -1), -1)
                                
                                predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])
                            else:
                                predict_x = pos_x[1] + linear_move(frame_delay - n_frames_change , 0, -1)
                                predict_y = pos_y[1] 

                        elif action == 3:
                            if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                                predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) 
                                
                                predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), 1)
                            
                            elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8:
                                predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) 
                                
                                predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), 1), 1)
                            
                            else:
                                predict_x = pos_x[1]
                                predict_y = pos_y[1] + linear_move(frame_delay - n_frames_change , 0, 1)

                        elif action == 4:
                            if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                                predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) 
                                
                                predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), -1)

                            elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                                predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) 
                                
                                predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), -1), -1)

                            else:
                                predict_x = pos_x[1]
                                predict_y = pos_y[1] + linear_move(frame_delay - n_frames_change , 0, -1)


                        elif action == 5:
                            if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                                predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), -1), -1)
                                
                                predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), 1), 1)
                            
                            elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                                predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), -1)
                                
                                predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), 1)
                            else:
                                predict_x = pos_x[1] + nonlinear_move(frame_delay - n_frames_change , 0, -1)
                                predict_y = pos_y[1] + nonlinear_move(frame_delay - n_frames_change , 0, 1)

                        elif action == 6:
                            if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                                predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), 1), 1)
                                
                                predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), 1), 1)

                            elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                                predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), 1)
                                
                                predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), 1)

                            else:
                                predict_x = pos_x[1] + nonlinear_move(frame_delay - n_frames_change , 0, 1)
                                predict_y = pos_y[1] + nonlinear_move(frame_delay - n_frames_change , 0, 1)

                        elif action == 7:
                            if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                                predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), -1), -1)
                                
                                predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), -1), -1)   
                            
                            elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8:
                                predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), -1)
                                
                                predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), -1)   
                            
                            else:
                                predict_x = pos_x[1] + nonlinear_move(frame_delay - n_frames_change , 0, -1)
                                predict_y = pos_y[1] + nonlinear_move(frame_delay - n_frames_change , 0, -1)                    

                        elif action == 8:
                            if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                                predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), 1), 1)
                                
                                predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), -1), -1)
                            
                            elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8:
                                predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), 1)
                                
                                predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), -1)
                            
                            else:
                                predict_x = pos_x[1] + nonlinear_move(frame_delay - n_frames_change , 0, 1)
                                predict_y = pos_y[1] + nonlinear_move(frame_delay - n_frames_change , 0, -1)

                    last_action = action
                    
                    data = str(predict_x) + "," + position_y + "," + str(predict_y) 
                    print("send message: ", data)

                    predict_data = data.encode("utf-8")
                    print(predict_data)
                    # print("Unity client", cli_data, data)
                    print("Unity client", cli_data)
                    unity_sock.sendto(predict_data, unity_addr)


                    # with open(f'{evaluate_dir}/no_delay_log.csv', 'a') as f:
                    # with open(f'{evaluate_dir}/no_delay_log_lerpumclamped2.csv', 'a') as f:
                    # with open(f'{evaluate_dir}/no_delay_log_interpolate.csv', 'a') as f:
                    # with open(f'{evaluate_dir}/no_delay_log_lerp2.csv', 'a') as f:
                    #     writer = csv.writer(f, lineterminator='\n')
                    #     writer.writerow([send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z])
                        # writer.writerow([send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, predict_x])

                    with open(f"{evaluate_dir}/delay_log.csv", 'a') as f:
                        writer = csv.writer(f, lineterminator='\n')
                        writer.writerow([float(send_time), float(position_x), float(position_y), float(position_z)])

                    # end = time.time()
                    # exe_time = end - start
                    # print(start, end, exe_time) #0.003

            elif Dflag == "predict":
                with open(f"{evaluate_dir}/predict_log.csv", 'a') as f:
                    writer = csv.writer(f, lineterminator='\n')
                    writer.writerow([float(send_time), float(position_x), float(position_y), float(position_z)])
    
        except KeyboardInterrupt:
            print ('\n . . .\n')
            cli_sock.close()
            unity_sock.close()

    

if __name__ == "__main__":
    main()