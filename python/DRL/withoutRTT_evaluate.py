from __future__ import print_function
import argparse

import numpy as np
from numpy.lib.function_base import diff
import torch
from torch import distributions, nn

import pfrl
from pfrl import agents, explorers, replay_buffers, utils
from pfrl import nn as pnn
from pfrl.q_functions import DistributionalFCStateQFunctionWithDiscreteAction


from argparse import ArgumentParser
from time import sleep
import csv
import datetime

import cv2

import logging

import skimage.color, skimage.transform

from gym.spaces import Box

import os
from datetime import datetime

from PIL import Image

import torch.nn.functional as F

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
    motions = ["ohuku", "curb", "zigzag", "ohukuRandom"]
    # motion = motions[0]
    motion = motions[3]
    delays = [25, 50, 75, 100]

    for half_delay in delays:
        log_dir = f'/mnt/HDD/Photon_FPS/DRLModels/{motion}/{frame_delay}/evaluate'
        model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/{motion}/0.2/20220603-17:42:07'

        delay = half_delay*2*0.001
        
        os.makedirs(log_dir, exist_ok=True)

        parser = ArgumentParser()
        parser.add_argument("-change_model")
        parser.add_argument("-act_model")

        args = parser.parse_args()

        logging.basicConfig(level=20)

        # Set a random seed used in PFRL.
        utils.set_random_seed(0)

        n_dim_obs = 20
        # n_dim_obs = 12
        # n_actions = 2
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
        change_agent.load(f'{model_dir}/change_model{args.change_model}')


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
        act_agent.load(f'{model_dir}/act_model{args.act_model}')

        # n_input = 12
        n_input = 20

        cpu_positions = {}
        cpu_velocity = {}
        cpu_keys = []

        # with open(f'/mnt/HDD/Photon_FPS/Log/Lag0/{motion}/Cpu_0608_1646.csv') as f:
        with open(f'/mnt/HDD/Photon_FPS/Log/Lag0/{motion}/Cpu_0608_1641.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                row[0] = float(row[0])
                for k in range(1, 7):
                    row[k] = float(row[k])
                cpu_positions[row[0]] = [row[1], row[2], row[3]]
                cpu_velocity[row[0]] = [row[4], row[5], row[6]]
                # time, x, z, y
                cpu_keys.append(float(row[0]))

        player_positions = {}
        player_velocity = {}
        player_keys = []

        # with open(f'/mnt/HDD/Photon_FPS/Log/Lag0/{motion}/Player_0608_1646.csv') as f:
        with open(f'/mnt/HDD/Photon_FPS/Log/Lag0/{motion}/Player_0608_1641.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                row[0] = float(row[0])
                for k in range(1, 7):
                    row[k] = float(row[k])
                player_positions[row[0]] = [row[1], row[2], row[3]]
                player_velocity[row[0]] = [row[4], row[5], row[6]]
                # time, x, z, y
                player_keys.append(float(row[0]))

        action = 0
        # 0->right 1->left
        n_frames_change = 0

        player_length = len(player_keys)
        cpu_length = len(cpu_keys)
        
        obs = np.zeros(n_input, dtype=np.float32)

        last_position_x = np.zeros(4)
        last_position_y = np.zeros(4)
        last_velocity_x = np.zeros(4)
        last_velocity_y = np.zeros(4)
        last_time = np.zeros(4)

        last_action = 0

        delay_diff_x = []
        delay_diff_y = []
        delay_diff = []

        mlp_diff_x = []
        mlp_diff_y = []
        mlp_diffs = []

        
        cpu_index = 0

        for key in player_keys:

            last_position_x = np.roll(last_position_x, 1)
            last_position_y = np.roll(last_position_y, 1)
            last_velocity_x = np.roll(last_velocity_x, 1)
            last_velocity_y = np.roll(last_velocity_y, 1)
            last_time = np.roll(last_time, 1)

            last_time[0] = key
            last_position_x[0] = player_positions[key][0]
            last_position_y[0] = player_positions[key][2]
            last_velocity_x[0] = player_velocity[key][0]
            last_velocity_y[0] = player_velocity[key][2]

            fps = last_time[0] - last_time[1]

            obs = [last_time[0], last_position_x[0], last_position_y[0], last_velocity_x[0], last_velocity_y[0], last_time[1], last_position_x[1], last_position_y[1], last_velocity_x[1], last_velocity_y[1], last_time[2], last_position_x[2], last_position_y[2], last_velocity_x[2], last_velocity_y[2], last_time[3], last_position_x[3], last_position_y[3], last_velocity_x[3], last_velocity_y[3]]

            if player_keys.index(key) < 4:
                continue
            else:
                obs = [last_time[0], last_position_x[0], last_position_y[0], last_velocity_x[0], last_velocity_y[0], last_time[1], last_position_x[1], last_position_y[1], last_velocity_x[1], last_velocity_y[1], last_time[2], last_position_x[2], last_position_y[2], last_velocity_x[2], last_velocity_y[2], last_time[3], last_position_x[3], last_position_y[3], last_velocity_x[3], last_velocity_y[3]]

                action = act_agent.act(obs)
                n_frames_change = change_agent.act(obs)

                player_index = player_keys.index(key)
                predict_point = key+delay
                last_cpu_index = cpu_index
                
                while True:
                    if cpu_keys[cpu_index] == predict_point:
                        break
                    elif cpu_keys[cpu_index] < predict_point:
                        cpu_index += 1
                    else:
                        ax, bx = calculateLine(cpu_positions[cpu_keys[cpu_index]][0], cpu_positions[cpu_keys[cpu_index-1]][0], cpu_keys[cpu_index], cpu_keys[cpu_index-1])
                        ay, by = calculateLine(cpu_positions[cpu_keys[cpu_index]][2], cpu_positions[cpu_keys[cpu_index-1]][2], cpu_keys[cpu_index], cpu_keys[cpu_index-1])
                        break

                if player_index >= player_length - n_frames or cpu_index >= cpu_length - n_frames:
                    break

                if ax == 0:
                    real_position_x = bx
                else:
                    real_position_x = (predict_point-bx) / ax 

                if ay == 0:
                    real_position_y = by
                else:
                    real_position_y = (predict_point-bx) / ay 

                delay_x = abs(real_position_x - last_position_x[0])
                delay_y = abs(real_position_y - last_position_y[0])
                diff = math.sqrt(delay_x ** 2 + delay_y ** 2)

                delay_diff_x.append(delay_x)
                delay_diff_y.append(delay_y)
                delay_diff.append(diff)

                frame_delay = delay / fps

                if n_frames_change > frame_delay:
                    if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                        predict_x = last_position_x[0] + linear_move(frame_delay, last_velocity_x[0] * linear_speed, last_velocity_x[0])
                        predict_y = last_position_y[0] + linear_move(frame_delay, last_velocity_y[0] * linear_speed, last_velocity_y[0])
                    elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                        predict_x = last_position_x[0] + nonlinear_move(frame_delay, last_velocity_x[0] * linear_speed, last_velocity_x[0])
                        predict_y = last_position_y[0] + nonlinear_move(frame_delay, last_velocity_y[0] * linear_speed, last_velocity_y[0])
                    else:
                        predict_x = last_position_x[0]
                        predict_y = last_position_y[0]

                else:
                    if action == 0:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = last_position_x[0] + linear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0])

                            predict_y = last_position_y[0] + linear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0])
                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                            predict_x = last_position_x[0] + nonlinear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0])
                            
                            predict_y = last_position_y[0] + nonlinear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0])
                        else:
                            predict_x = last_position_x[0]
                            predict_y = last_position_y[0]

                    elif action == 1:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = last_position_x[0] + linear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]), 1)
                            
                            predict_y = last_position_y[0] + linear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0])

                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8:  
                            predict_x = last_position_x[0] + nonlinear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, last_velocity_x[0] * linear_speed, last_velocity_x[0]), 1) , 1)
                            
                            predict_y = last_position_y[0] + nonlinear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0])

                        else:
                            predict_x = last_position_x[0] + linear_move(frame_delay - n_frames_change , 0, 1)
                            predict_y = last_position_y[0]

                    elif action == 2:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = last_position_x[0] + linear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]), -1)
                            
                            predict_y = last_position_y[0] + linear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0])
                        
                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                            predict_x = last_position_x[0] + nonlinear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, last_velocity_x[0] * linear_speed, last_velocity_x[0]), -1), -1)
                            
                            predict_y = last_position_y[0] + nonlinear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0])
                        else:
                            predict_x = last_position_x[0] + linear_move(frame_delay - n_frames_change , 0, -1)
                            predict_y = last_position_y[0] 

                    elif action == 3:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = last_position_x[0] + linear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) 
                            
                            predict_y = last_position_y[0] + linear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]), 1)
                        
                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8:
                            predict_x = last_position_x[0] + nonlinear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) 
                            
                            predict_y = last_position_y[0] + nonlinear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, last_velocity_y[0] * linear_speed, last_velocity_y[0]), 1), 1)
                        
                        else:
                            predict_x = last_position_x[0]
                            predict_y = last_position_y[0] + linear_move(frame_delay - n_frames_change , 0, 1)

                    elif action == 4:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = last_position_x[0] + linear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) 
                            
                            predict_y = last_position_y[0] + linear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + linear_move(frame_delay - n_frames_change , linear_velocity(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]), -1)

                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                            predict_x = last_position_x[0] + nonlinear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) 
                            
                            predict_y = last_position_y[0] + nonlinear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + linear_move(frame_delay - n_frames_change , linear_velocity(1, nonlinear_velocity(n_frames_change-1, last_velocity_y[0] * linear_speed, last_velocity_y[0]), -1), -1)

                        else:
                            predict_x = last_position_x[0]
                            predict_y = last_position_y[0] + linear_move(frame_delay - n_frames_change , 0, -1)


                    elif action == 5:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = last_position_x[0] + linear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, last_velocity_x[0] * linear_speed, last_velocity_x[0]), -1), -1)
                            
                            predict_y = last_position_y[0] + linear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, last_velocity_y[0] * linear_speed, last_velocity_y[0]), 1), 1)
                        
                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                            predict_x = last_position_x[0] + nonlinear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]), -1)
                            
                            predict_y = last_position_y[0] + nonlinear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]), 1)
                        else:
                            predict_x = last_position_x[0] + nonlinear_move(frame_delay - n_frames_change , 0, -1)
                            predict_y = last_position_y[0] + nonlinear_move(frame_delay - n_frames_change , 0, 1)

                    elif action == 6:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = last_position_x[0] + linear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, last_velocity_x[0] * linear_speed, last_velocity_x[0]), 1), 1)
                            
                            predict_y = last_position_y[0] + linear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, last_velocity_y[0] * linear_speed, last_velocity_y[0]), 1), 1)

                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8: 
                            predict_x = last_position_x[0] + nonlinear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]), 1)
                            
                            predict_y = last_position_y[0] + nonlinear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]), 1)

                        else:
                            predict_x = last_position_x[0] + nonlinear_move(frame_delay - n_frames_change , 0, 1)
                            predict_y = last_position_y[0] + nonlinear_move(frame_delay - n_frames_change , 0, 1)

                    elif action == 7:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = last_position_x[0] + linear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, last_velocity_x[0] * linear_speed, last_velocity_x[0]), -1), -1)
                            
                            predict_y = last_position_y[0] + linear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, last_velocity_y[0] * linear_speed, last_velocity_y[0]), -1), -1)   
                        
                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8:
                            predict_x = last_position_x[0] + nonlinear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]), -1)
                            
                            predict_y = last_position_y[0] + nonlinear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]), -1)   
                        
                        else:
                            predict_x = last_position_x[0] + nonlinear_move(frame_delay - n_frames_change , 0, -1)
                            predict_y = last_position_y[0] + nonlinear_move(frame_delay - n_frames_change , 0, -1)                    

                    elif action == 8:
                        if last_action == 1 or last_action == 2 or last_action == 3 or last_action == 4:
                            predict_x = last_position_x[0] + linear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, last_velocity_x[0] * linear_speed, last_velocity_x[0]), 1), 1)
                            
                            predict_y = last_position_y[0] + linear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(1, linear_velocity(n_frames_change-1, last_velocity_y[0] * linear_speed, last_velocity_y[0]), -1), -1)
                        
                        elif last_action == 5 or last_action == 6 or last_action == 7 or last_action == 8:
                            predict_x = last_position_x[0] + nonlinear_move(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, last_velocity_x[0] * linear_speed, last_velocity_x[0]), 1)
                            
                            predict_y = last_position_y[0] + nonlinear_move(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]) + nonlinear_move(frame_delay - n_frames_change , nonlinear_velocity(n_frames_change, last_velocity_y[0] * linear_speed, last_velocity_y[0]), -1)
                        
                        else:
                            predict_x = last_position_x[0] + nonlinear_move(frame_delay - n_frames_change , 0, 1)
                            predict_y = last_position_y[0] + nonlinear_move(frame_delay - n_frames_change , 0, -1)

                mlp_x = abs(positions[keys[index + frame_delay - 1]][0] - predict_x)
                mlp_y = abs(positions[keys[index + frame_delay - 1]][2] - predict_y)
                mlp_diff = math.sqrt(mlp_x ** 2 + mlp_y ** 2)

                mlp_diff_x.append(mlp_x)
                mlp_diff_y.append(mlp_y)
                mlp_diffs.append(mlp_diff)   
            
            move_xdir = velocity[key][0]
            move_ydir = velocity[key][2] #fixed

            if move_xdir > 0 and move_ydir == 0:
                last_action = 1
            elif move_xdir < 0 and move_ydir == 0:
                last_action = 2
            elif move_xdir == 0 and move_ydir > 0:
                last_action = 3
            elif move_xdir == 0 and move_ydir < 0:
                last_action = 4
            elif move_xdir < 0 and move_ydir > 0:
                last_action = 5
            elif move_xdir < 0 and move_ydir < 0:
                last_action = 7
            elif move_xdir > 0 and move_ydir > 0:
                last_action = 6
            elif move_xdir > 0 and move_ydir < 0:
                last_action = 8
            else:
                last_action = 0

            last_position_x = np.roll(last_position_x, 1)
            last_position_y = np.roll(last_position_y, 1)
            last_velocity_x = np.roll(last_velocity_x, 1)
            last_velocity_y = np.roll(last_velocity_y, 1)
            last_time = np.roll(last_time, 1)

            last_time[0] = key
            last_position_x[0] = positions[key][0]
            last_position_y[0] = positions[key][2]
            last_velocity_x[0] = velocity[key][0]
            last_velocity_y[0] = velocity[key][2]

        average_diff_x = sum(delay_diff_x)/len(delay_diff_x)
        average_diff_y = sum(delay_diff_y)/len(delay_diff_y)
        average_diff = sum(delay_diff)/len(delay_diff)


        average_mlp_diff_x = sum(mlp_diff_x)/len(mlp_diff_x)
        average_mlp_diff_y = sum(mlp_diff_y)/len(mlp_diff_y)
        average_mlp_diff = sum(mlp_diffs)/len(mlp_diffs)

        print("Episode finished!")
        print("average diff: ", average_diff)
        print("average mlp diff: ", average_mlp_diff)

        with open(f'{log_dir}/diff_result.csv', 'a') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow([frame_delay, average_diff_x, average_diff_y, average_diff, average_mlp_diff_x, average_mlp_diff_y, average_mlp_diff])

        print(f"frame{frame_delay} finish")
        print("=====================")


if __name__ == "__main__":
    main()