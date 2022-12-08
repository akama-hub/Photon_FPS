from __future__ import print_function
# from turtle import delay, distance

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
from datetime import datetime
import time


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
    parser.add_argument("-o", "--obs", type=int)
    # parser.add_argument("-change_model", type=int)
    # parser.add_argument("-act_model", type=int)

    args = parser.parse_args()

    model_dir = ""
    # evaluate_dir = ""
    n_dim_obs = args.obs

    # log_date = datetime.now().strftime("%Y%m%d")

    # ubuntu garellia
    if args.motion == "ohuku":
        if n_dim_obs == 20:
            model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/Fixed30FPS_SendRate60_RTT/Lag20/{args.motion}/t_Pxz_Vxz'
            model_num = 8501
    elif args.motion == "curb":
        model = "20220726-15:31:08_SendRate60"
        model_num = 9501
    elif args.motion == "ohukuRandom":
        model_num = 9501

        if n_dim_obs == 20:
            # model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/Fixed30FPS_SendRate60_RTT/Lag20/{args.motion}/t_Pxz_Vxz/20221111-13:38:26'
            model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/Fixed30FPS_SendRate60_RTT/Lag20/{args.motion}/t_Pxz_Vxz/20221114-12:17:09'
            # evaluate_dir = f"../evaluate{log_date}/chamfer/Fixed30FPS_SendRate60_RTT/Lag{args.latency}/{args.motion}/t_Pxz_Vxz"
        
        elif n_dim_obs == 21:
            # model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/Fixed30FPS_SendRate60_RTT/Lag20/{args.motion}/t_Pxz_Vxz_distance/20221111-13:38:27'
            model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/Fixed30FPS_SendRate60_RTT/Lag20/{args.motion}/t_Pxz_Vxz_distance/20221114-12:17:11'
            # evaluate_dir = f"../evaluate{log_date}/chamfer/Fixed30FPS_SendRate60_RTT/Lag{args.latency}/{args.motion}/t_Pxz_Vxz_distance"

        elif n_dim_obs == 17:
            # model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/Fixed30FPS_SendRate60_RTT/Lag20/{args.motion}/Pxz_Vxz_distance/20221111-13:38:38'
            model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/Fixed30FPS_SendRate60_RTT/Lag20/{args.motion}/Pxz_Vxz_distance/20221114-12:17:06'
            # evaluate_dir = f"../evaluate{log_date}/chamfer/Fixed30FPS_SendRate60_RTT/Lag{args.latency}/{args.motion}/Pxz_Vxz_distance"

        elif n_dim_obs == 16:
            # model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/Fixed30FPS_SendRate60_RTT/Lag20/{args.motion}/Pxz_Vxz/20221111-13:39:21'
            model_dir = f'/mnt/HDD/Photon_FPS/DRLModels/Fixed30FPS_SendRate60_RTT/Lag20/{args.motion}/Pxz_Vxz/20221114-12:17:14'
            # evaluate_dir = f"../evaluate{log_date}/chamfer/Fixed30FPS_SendRate60_RTT/Lag{args.latency}/{args.motion}/Pxz_Vxz"

    elif args.motion == "zigzag":
        model = "20220623-13:17:15"
        model_num = 9901

    # model_dir =f'../../DRLModels/{args.motion}/{model}'

    
    # evaluate_dir = f"../evaluate/EvaluateDiffLog/Lag{args.latency}/{args.motion}/Proposed2"
    # evaluate_dir = f"../evaluate{log_date}/chamfer/Fixed30FPS_SendRate60_RTT/Lag{args.latency}/{args.motion}/DRL_distance"

    # os.makedirs(evaluate_dir, exist_ok=True)

    # home pc
    # model_dir =f'../../DRLModels/{motion}/'

    logging.basicConfig(level=20)

    # Set a random seed used in PFRL.
    utils.set_random_seed(0)

    # n_dim_obs = 21
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

            cli_data, cli_addr = cli_sock.recvfrom(M_SIZE)
            # clidata = time00000000x00000000y00000000z00000000
            #　負の値を取るとーも一文字になるので注意
            cli_str_data = cli_data.decode("utf-8")
            # print("recieving data: ", cli_data)

            rcv_data = cli_str_data.split(',')
            
            if cnt < 20:
                pos_x[0] = float(rcv_data[1])
                pos_y[0] = float(rcv_data[2])
                vel_x[0] = float(rcv_data[3])
                vel_y[0] = float(rcv_data[4])
                t[0] = float(rcv_data[0])

                cnt += 1

            else:
                pos_x = np.roll(pos_x, 1)
                pos_y = np.roll(pos_y, 1)
                vel_x = np.roll(vel_x, 1)
                vel_y = np.roll(vel_y, 1)
                t = np.roll(t, 1)

                pos_x[0] = float(rcv_data[1])
                pos_y[0] = float(rcv_data[2])
                vel_x[0] = float(rcv_data[3])
                vel_y[0] = float(rcv_data[4])
                t[0] = float(rcv_data[0])

                distance = float(rcv_data[5])

                obs = [t[0], pos_x[0], pos_y[0], vel_x[0], vel_y[0], t[1], pos_x[1], pos_y[1], vel_x[1], vel_y[1], t[2], pos_x[2], pos_y[2], vel_x[2], vel_y[2], t[3], pos_x[3], pos_y[3], vel_x[3], vel_y[3], distance]

                if n_dim_obs == 20:
                    obs = [t[0], pos_x[0], pos_y[0], vel_x[0], vel_y[0], t[1], pos_x[1], pos_y[1], vel_x[1], vel_y[1], t[2], pos_x[2], pos_y[2], vel_x[2], vel_y[2], t[3], pos_x[3], pos_y[3], vel_x[3], vel_y[3]]
                
                elif n_dim_obs == 21:
                    obs = [t[0], pos_x[0], pos_y[0], vel_x[0], vel_y[0], t[1], pos_x[1], pos_y[1], vel_x[1], vel_y[1], t[2], pos_x[2], pos_y[2], vel_x[2], vel_y[2], t[3], pos_x[3], pos_y[3], vel_x[3], vel_y[3], distance]

                elif n_dim_obs == 17:
                    obs = [pos_x[0], pos_y[0], vel_x[0], vel_y[0], pos_x[1], pos_y[1], vel_x[1], vel_y[1], pos_x[2], pos_y[2], vel_x[2], vel_y[2], pos_x[3], pos_y[3], vel_x[3], vel_y[3], distance]

                elif n_dim_obs == 16:
                    obs = [pos_x[0], pos_y[0], vel_x[0], vel_y[0], pos_x[1], pos_y[1], vel_x[1], vel_y[1], pos_x[2], pos_y[2], vel_x[2], vel_y[2], pos_x[3], pos_y[3], vel_x[3], vel_y[3]]
                
                action = act_agent.act(obs)
                n_frames_change = change_agent.act(obs)
                
                data = str(n_frames_change) + "," +  str(action)
                # print("send message: ", data)

                predict_data = data.encode("utf-8")
                # print("Sending data: ", predict_data)
                # print("Unity client", cli_data, data)
                # print("Unity client", cli_data)
                unity_sock.sendto(predict_data, unity_addr)

                # end = time.time()
                # exe_time = end - start
                # print("execute time: ", exe_time) #0.003
                
                # with open(f"{evaluate_dir}/Delayed_log.csv", 'a') as f:
                #     writer = csv.writer(f, lineterminator='\n')
                #     writer.writerow(rcv_data)
    
        except KeyboardInterrupt:
            print ('\n . . .\n')
            cli_sock.close()
            unity_sock.close()

    

if __name__ == "__main__":
    main()