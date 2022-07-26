from __future__ import print_function
import argparse
from turtle import distance

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
    motions = ["ohuku", "curb", "zigzag", "ohukuRandom"]
    # motion = motions[0]
    motion = motions[1]
    # motion = motions[2]
    # motion = motions[3]

    delay = 0.15

    log_date = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    log_dir = f'/mnt/HDD/Photon_FPS/DRLModels/{motion}/{log_date}_different_send'

    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(level=20)

    # Set a random seed used in PFRL.
    utils.set_random_seed(0)

    # n_dim_obs = 20
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

    n_input = 20
    episodes = 10000

    cpu_positions = {}
    cpu_velocity = {}
    cpu_keys = []

    # with open(f'/mnt/HDD/Photon_FPS/Log/Lag0/{motion}/{cpu_log}') as f:
    # with open(f'../evaluate/EvaluateDiffLog/LagNone/{motion}/train/real_log_train.csv') as f:
    with open(f'../train_data/Fixed30FPS/Lag25/{motion}/Real_log.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            row[0] = float(row[0])
            for k in range(1, 7):
                row[k] = float(row[k])
            cpu_positions[row[0]] = [row[1], row[2], row[3]]
            cpu_velocity[row[0]] = [row[4], row[5], row[6]]
            # time, x, z, y
            cpu_keys.append(row[0])

    player_positions = {}
    player_velocity = {}
    player_keys = []
    distance = {}

    # with open(f'/mnt/HDD/Photon_FPS/Log/Lag0/{motion}/{player_log}') as f:
    # with open(f'../evaluate/EvaluateDiffLog/LagNone/{motion}/train/delayed_log_train.csv') as f:
        # reader = csv.reader(f)
        # for row in reader:
            # row[0] = float(row[0])
            # for k in range(1, 7):
            #     row[k] = float(row[k])
            # cpu_positions[row[0]] = [row[1], row[2], row[3]]
            # cpu_velocity[row[0]] = [row[4], row[5], row[6]]
            # # time, x, z, y
            # cpu_keys.append(row[0])
    with open(f'../train_data/Fixed30FPS/Lag25/{motion}/Delayed_log.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            row[1] = float(row[1])
            for k in range(2, 7):
                row[k] = float(row[k])
            if row[10] == "true":
                player_positions[row[1]] = [row[2], row[3], row[4]]
                player_velocity[row[1]] = [row[5], row[6], row[7]]
                # time, x, z, y
                distance[row[1]] = float(row[9])
                player_keys.append(row[1])

    action = 0
    # 0->right 1->left
    n_frames_change = 0

    player_length = len(player_keys)
    cpu_length = len(cpu_keys)

    for episode in range(episodes):
        # obs4steps = np.zeros((n_past, n_input), dtype=np.float32)
        obs = np.zeros(n_input, dtype=np.float32)
        action_R = 0
        change_R = 0
        change1 = 0
        change2 = 0
        max_R_action = 0
        max_R_change = 0
        max_change1 = 0
        max_change2 = 0

        last_position_x = np.zeros(4)
        last_position_y = np.zeros(4)
        last_velocity_x = np.zeros(4)
        last_velocity_y = np.zeros(4)
        last_time = np.zeros(4)

        cpu_index = 0

        for key in player_keys:
            action_reward = 0
            change_reward = 0
            actual_change_frame = 0
            actual_action = 0

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

            if player_keys.index(key) < 8:
                continue
            else:
                obs = [last_time[0], last_position_x[0], last_position_y[0], last_velocity_x[0], last_velocity_y[0], last_time[1], last_position_x[1], last_position_y[1], last_velocity_x[1], last_velocity_y[1], last_time[2], last_position_x[2], last_position_y[2], last_velocity_x[2], last_velocity_y[2], last_time[3], last_position_x[3], last_position_y[3], last_velocity_x[3], last_velocity_y[3], distance[key]]

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
                        # ax, bx = calculateLine(cpu_positions[cpu_keys[cpu_index]][0], cpu_positions[cpu_keys[cpu_index-1]][0], cpu_keys[cpu_index], cpu_keys[cpu_index-1])
                        # ay, by = calculateLine(cpu_positions[cpu_keys[cpu_index]][2], cpu_positions[cpu_keys[cpu_index-1]][2], cpu_keys[cpu_index], cpu_keys[cpu_index-1])
                        cpu_index -= 1
                        break

                if player_index >= player_length - n_frames or cpu_index >= cpu_length - n_frames:
                    break
                
                for i in range(10):
                    pre_action = get_action_num(cpu_velocity[cpu_keys[last_cpu_index+i-1]][0], cpu_velocity[cpu_keys[last_cpu_index+i-1]][2])

                    next_action = get_action_num(cpu_velocity[cpu_keys[last_cpu_index+i]][0], cpu_velocity[cpu_keys[last_cpu_index+i]][2])

                    if pre_action != next_action:
                        actual_change_frame = i
                        actual_action = next_action
                        break
                    else:
                        actual_change_frame = 0
                        actual_action = next_action

                if actual_change_frame == 0:
                    max_R_change += 1
                    max_change1 += 1
                    if actual_change_frame == n_frames_change:
                        change_reward = 1
                        change1 += 1
                    else:
                        change_reward = 0
                else:
                    max_R_change += 10
                    max_change2 += 1
                    if actual_change_frame == n_frames_change:
                        change_reward = 10
                        change2 += 1
                    else:
                        change_reward = 0
                
                max_R_action += 1
                if actual_action == action:
                    action_reward = 1

                action_R += action_reward
                change_R += change_reward

                done = False
                reset = False

                change_agent.observe(obs, change_reward, done, reset)
                act_agent.observe(obs, action_reward, done, reset)

                with open(f'{log_dir}/check.csv', 'a') as f:
                    f.write(f'{episode}, {action}, {actual_action},{n_frames_change}, {actual_change_frame}, {action_reward}, {change_reward} \n')

        done = True
        reset = True

        change_agent.observe(obs, change_reward, done, reset)
        act_agent.observe(obs, action_reward, done, reset)

        print("Episode finished!")
        print("Episode: ", episode)
        print(f"total action reward: {action_R} / {max_R_action}")
        print(f"total change reward: {change_R} / {max_R_change}")
        print(f"successing point: {change1} / {max_change1}")
        print(f"changing point: {change2} / {max_change2}")
        print("=====================")

        with open(f'{log_dir}/result.csv', 'a') as f:
            f.write(f'{episode + 1}, {max_R_action}, {action_R}, {max_R_change}, {change_R}\n')

        if episode % 500 == 0 and episode >= 2000:
            change_agent.save(f"{log_dir}/change_model{episode+1}")
            act_agent.save(f"{log_dir}/act_model{episode+1}")

if __name__ == "__main__":
    main()