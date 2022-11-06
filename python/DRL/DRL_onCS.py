import sys #引数を得るために使用

from __future__ import print_function
import argparse
from turtle import delay, distance

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

import math
from datetime import datetime
import time

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

def get_action_num(x, y):
    if x > 0:
        if y == 0:
            action = 0
        elif y > 0:
            action = 1
        else:
            action = 7
    if x < 0:
        if y == 0:
            action = 4
        elif y > 0:
            action = 3
        else:
            action = 5
    if x == 0:
        if y == 0:
            action = 8
        elif y > 0:
            action = 2
        else:
            action = 6
    return action

def main():

    pos_x = np.zeros(4)
    pos_y = np.zeros(4)
    vel_x = np.zeros(4)
    vel_y = np.zeros(4)
    t = np.zeros(4)

    motion = "ohuku"
    latency = 10

    # ubuntu garellia
    if motion == "ohuku":
        model = "20220726-15:31:46_SendRate60"
        model_num = 9501
    elif motion == "curb":
        model = "20220726-15:31:08_SendRate60"
        model_num = 9501
    elif motion == "ohukuRandom":
        model = "20220611-13:50:55"
        model_num = 3301
    elif motion == "zigzag":
        model = "20220623-13:17:15"
        model_num = 9901

    model_dir =f'../../DRLModels/{motion}/{model}'

    log_date = datetime.now().strftime("%Y%m%d")
    # evaluate_dir = f"../evaluate/EvaluateDiffLog/Lag{args.latency}/{args.motion}/Proposed2"
    evaluate_dir = f"../evaluate{log_date}/chamfer/Fixed30FPS_SendRate60_RTT/Lag{latency}/{motion}/DRL_distance"
    os.makedirs(evaluate_dir, exist_ok=True)

    logging.basicConfig(level=20)

    # Set a random seed used in PFRL.
    utils.set_random_seed(0)

    n_dim_obs = 21
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

    # arguments from cs(time, x, y, vx, vy, distance, delay)

    if cnt < 8:
        pos_x[0] = float(rcv_data[2])
        pos_y[0] = float(rcv_data[4])
        vel_x[0] = float(rcv_data[5])
        vel_y[0] = float(rcv_data[7])
        t[0] = float(rcv_data[1])

        cnt += 1

    else:
        pos_x = np.roll(pos_x, 1)
        pos_y = np.roll(pos_y, 1)
        vel_x = np.roll(vel_x, 1)
        vel_y = np.roll(vel_y, 1)
        t = np.roll(t, 1)

        pos_x[0] = float(rcv_data[2])
        pos_y[0] = float(rcv_data[4])
        vel_x[0] = float(rcv_data[5])
        vel_y[0] = float(rcv_data[7])
        t[0] = float(rcv_data[1])

        distance = float(rcv_data[9])

        obs = [t[0], pos_x[0], pos_y[0], vel_x[0], vel_y[0], t[1], pos_x[1], pos_y[1], vel_x[1], vel_y[1], t[2], pos_x[2], pos_y[2], vel_x[2], vel_y[2], t[3], pos_x[3], pos_y[3], vel_x[3], vel_y[3], distance]
        
        action = act_agent.act(obs)
        n_frames_change = change_agent.act(obs)
        
        fps = 0.033
        # delay = float(rcv_data[8]) + 0.032
        delay = float(rcv_data[10]) + 0.033

        frame_delay = round(delay/fps)

        if n_frames_change > frame_delay:
            if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                predict_x = pos_x[1] + linear_move(frame_delay, vel_x[1] * linear_speed, vel_x[1])
                predict_y = pos_y[1] + linear_move(frame_delay, vel_y[1] * linear_speed, vel_y[1])
            elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7: 
                predict_x = pos_x[1] + nonlinear_move(frame_delay, vel_x[1] * linear_speed, vel_x[1])
                predict_y = pos_y[1] + nonlinear_move(frame_delay, vel_y[1] * linear_speed, vel_y[1])
            else:
                predict_x = pos_x[1]
                predict_y = pos_y[1]

        else:
            if action == 8:
                if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                    predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1])

                    predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])
                elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7: 
                    predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1])
                    
                    predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])
                else:
                    predict_x = pos_x[1]
                    predict_y = pos_y[1]

            elif action == 0:
                if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                    predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), 1)
                    
                    predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])

                elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7:  
                    predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), 1) , 1)
                    
                    predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])

                else:
                    predict_x = pos_x[1] + linear_move(frame_delay - n_frames_change , 0, 1)
                    predict_y = pos_y[1]

            elif action == 4:
                if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                    predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), -1)
                    
                    predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])
                
                elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7: 
                    predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), -1), -1)
                    
                    predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1])
                else:
                    predict_x = pos_x[1] + linear_move(frame_delay - n_frames_change , 0, -1)
                    predict_y = pos_y[1] 

            elif action == 2:
                if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                    predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) 
                    
                    predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), 1)
                
                elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7:
                    predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) 
                    
                    predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), 1), 1)
                
                else:
                    predict_x = pos_x[1]
                    predict_y = pos_y[1] + linear_move(frame_delay - n_frames_change , 0, 1)

            elif action == 6:
                if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                    predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) 
                    
                    predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), -1)

                elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7: 
                    predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) 
                    
                    predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), -1), -1)

                else:
                    predict_x = pos_x[1]
                    predict_y = pos_y[1] + linear_move(frame_delay - n_frames_change , 0, -1)


            elif action == 3:
                if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                    predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), -1), -1)
                    
                    predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), 1), 1)
                
                elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7: 
                    predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), -1)
                    
                    predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), 1)
                else:
                    predict_x = pos_x[1] + nonlinear_move(frame_delay - n_frames_change , 0, -1)
                    predict_y = pos_y[1] + nonlinear_move(frame_delay - n_frames_change , 0, 1)

            elif action == 1:
                if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                    predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), 1), 1)
                    
                    predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), 1), 1)

                elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7: 
                    predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), 1)
                    
                    predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), 1)

                else:
                    predict_x = pos_x[1] + nonlinear_move(frame_delay - n_frames_change , 0, 1)
                    predict_y = pos_y[1] + nonlinear_move(frame_delay - n_frames_change , 0, 1)

            elif action == 5:
                if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                    predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), -1), -1)
                    
                    predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), -1), -1)   
                
                elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7:
                    predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), -1)
                    
                    predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), -1)   
                
                else:
                    predict_x = pos_x[1] + nonlinear_move(frame_delay - n_frames_change , 0, -1)
                    predict_y = pos_y[1] + nonlinear_move(frame_delay - n_frames_change , 0, -1)                    

            elif action == 7:
                if last_action == 0 or last_action == 2 or last_action == 4 or last_action == 6:
                    predict_x = pos_x[1] + linear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_x[1] * linear_speed, vel_x[1]), 1), 1)
                    
                    predict_y = pos_y[1] + linear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, vel_y[1] * linear_speed, vel_y[1]), -1), -1)
                
                elif last_action == 1 or last_action == 3 or last_action == 5 or last_action == 7:
                    predict_x = pos_x[1] + nonlinear_move(n_frames_change, vel_x[1] * linear_speed, vel_x[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_x[1] * linear_speed, vel_x[1]), 1)
                    
                    predict_y = pos_y[1] + nonlinear_move(n_frames_change, vel_y[1] * linear_speed, vel_y[1]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, vel_y[1] * linear_speed, vel_y[1]), -1)
                
                else:
                    predict_x = pos_x[1] + nonlinear_move(frame_delay - n_frames_change , 0, 1)
                    predict_y = pos_y[1] + nonlinear_move(frame_delay - n_frames_change , 0, -1)

        last_action = get_action_num(vel_x[0], vel_y[0])
                    
                    data = str(predict_x) + "," + rcv_data[3] + "," + str(predict_y) 
                    # print("send message: ", data)

                    predict_data = data.encode("utf-8")
                    print("Sending data: ", predict_data)
                    # print("Unity client", cli_data, data)
                    # print("Unity client", cli_data)
                    unity_sock.sendto(predict_data, unity_addr)

                    end = time.time()
                    exe_time = end - start
                    print("execute time: ", exe_time) #0.003

                    rcv_data.append(str(predict_x))
                    rcv_data.append(str(predict_y))
                    rcv_data.append(str(exe_time))
                    
                    with open(f"{evaluate_dir}/Delayed_log.csv", 'a') as f:
                        writer = csv.writer(f, lineterminator='\n')
                        writer.writerow(rcv_data)

    

if __name__ == "__main__":
    main()