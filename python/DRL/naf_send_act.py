from __future__ import print_function

import numpy as np
from numpy.lib.function_base import diff
import torch

from pfrl import agents, explorers, replay_buffers, utils
from pfrl import nn as pnn
from pfrl.q_functions import DistributionalFCStateQFunctionWithDiscreteAction, FCQuadraticStateQFunction

from time import sleep
import csv

import logging

import skimage.color, skimage.transform

from gym.spaces import Box

import os
from datetime import datetime

from PIL import Image

import torch.nn.functional as F

import socket
import signal

from argparse import ArgumentParser

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
    # ctrl-Cがなかなか反応しないのを直す
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    M_SIZE = 1024
    host = '127.0.0.1' 
    # 自分を指定
    serv_port = 50026
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

    if args.latency == 0:
        delay = 0.032
    elif args.latency == 10:
        delay = 0.064
    elif args.latency == 25:
        delay = 0.086

    processing_delay = 0.02

    model_dir =f'../../DRLModels/{args.motion}/{model}'

    evaluate_dir = f"../evaluate/EvaluateDiffLog/Lag{args.latency}/{args.motion}/NAF"
    os.makedirs(evaluate_dir, exist_ok=True)

    logging.basicConfig(level=20)

    # Set a random seed used in PFRL.
    utils.set_random_seed(0)

    n_delay = 150 # milisecond

    n_dim_obs = 20
    n_actions = 9
    action_space = Box(low=0.0, high=1.0, shape=(1,))
    action_size = action_space.low.size
    n_atoms = 51
    v_max = 10
    v_min = -10
    n_hidden_channels = 100
    n_hidden_layers = 3
    nonlinearity = F.relu
    last_wscale = 1.0
    
    change_q_func = FCQuadraticStateQFunction(n_dim_obs, action_size, n_hidden_channels, n_hidden_layers, action_space, True)
    """
    Args:
        n_input_channels: number of input channels
        n_dim_action: number of dimensions of action space
        n_hidden_channels: number of hidden channels
        n_hidden_layers: number of hidden layers
        action_space: action_space
        scale_mu (bool): scale mu by applying tanh if True
    """

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

    change_agent = agents.DQN(
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

    """"
    Args:
        q_function (StateQFunction): Q-function
        optimizer (Optimizer): Optimizer that is already setup
        replay_buffer (ReplayBuffer): Replay buffer
        gamma (float): Discount factor
        explorer (Explorer): Explorer that specifies an exploration strategy.
        gpu (int): GPU device id if not None nor negative.
        replay_start_size (int): if the replay buffer's size is less than
            replay_start_size, skip update
        minibatch_size (int): Minibatch size
        update_interval (int): Model update interval in step
        target_update_interval (int): Target model update interval in step
        clip_delta (bool): Clip delta if set True
        phi (callable): Feature extractor applied to observations
        target_update_method (str): 'hard' or 'soft'.
        soft_update_tau (float): Tau of soft target update.
        n_times_update (int): Number of repetition of update
        batch_accumulator (str): 'mean' or 'sum'
        episodic_update_len (int or None): Subsequences of this length are used
            for update if set int and episodic_update=True
        logger (Logger): Logger used
        batch_states (callable): method which makes a batch of observations.
            default is `pfrl.utils.batch_states.batch_states`
        recurrent (bool): If set to True, `model` is assumed to implement
            `pfrl.nn.Recurrent` and is updated in a recurrent
            manner.
        max_grad_norm (float or None): Maximum L2 norm of the gradient used for
            gradient clipping. If set to None, the gradient is not clipped.
    """

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

    while True:
        try:
            # start = time.time() #単位は秒

            # unity_sock.sendto("hi".encode("utf-8"), unity_addr)

            cli_data, cli_addr = cli_sock.recvfrom(M_SIZE)
            print("recieving data: ", cli_data)
            # clidata = time00000000x00000000y00000000z00000000
            #　負の値を取るとーも一文字になるので注意

            cli_str_data = cli_data.decode("utf-8")
            rcv_data = cli_str_data.split(',')
            
            
            if cnt < 4:
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

                obs = [t[0], pos_x[0], pos_y[0], vel_x[0], vel_y[0], t[1], pos_x[1], pos_y[1], vel_x[1], vel_y[1], t[2], pos_x[2], pos_y[2], vel_x[2], vel_y[2], t[3], pos_x[3], pos_y[3], vel_x[3], vel_y[3]]
                
                action = act_agent.act(obs)
                change_second = change_agent.act(obs)[0] * 0.2

                # lag = float(rcv_data[8]) + processing_delay

                
                data = str(action) + "," + str(change_second) 
                print("send message: ", data)

                # predict_data = data.encode("utf-8")
                # print(predict_data)
                # print("Unity client", cli_data, data)
                print("Unity client", cli_data)
                unity_sock.sendto(data.encode("utf-8"), unity_addr)


                 # with open(f'{evaluate_dir}/no_delay_log.csv', 'a') as f:
                # with open(f'{evaluate_dir}/no_delay_log_lerpumclamped2.csv', 'a') as f:
                # with open(f'{evaluate_dir}/no_delay_log_interpolate.csv', 'a') as f:
                # with open(f'{evaluate_dir}/no_delay_log_lerp2.csv', 'a') as f:
                #     writer = csv.writer(f, lineterminator='\n')
                #     writer.writerow([rcv_data[1], rcv_data[2], rcv_data[3], rcv_data[4], rcv_data[5], velocity_y, rcv_data[7]])
                    # writer.writerow([rcv_data[1], rcv_data[2], rcv_data[3], rcv_data[4], rcv_data[5], velocity_y, rcv_data[7], predict_x])

                with open(f"{evaluate_dir}/real_log.csv", 'a') as f:
                    writer = csv.writer(f, lineterminator='\n')
                    writer.writerow([float(rcv_data[1]), float(rcv_data[2]), float(rcv_data[3]), float(rcv_data[4])])

                # end = time.time()
                # exe_time = end - start
                # print(start, end, exe_time) #0.003
    
        except KeyboardInterrupt:
            print ('\n . . .\n')
            cli_sock.close()
            unity_sock.close()

if __name__ == "__main__":
    main()