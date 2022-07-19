from __future__ import print_function
from turtle import forward

import numpy as np
from numpy.lib.function_base import diff
import torch
from torch import distributions, float32, float64, nn

import pfrl
from pfrl import agents, explorers, replay_buffers, utils
from pfrl import nn as pnn
from pfrl.q_functions import DistributionalFCStateQFunctionWithDiscreteAction

from argparse import ArgumentParser
from time import sleep
import csv
import datetime

import logging

import skimage.color, skimage.transform

from gym.spaces import Box

import os
from datetime import datetime

from pfrl.nn.lmbda import Lambda

import torch.nn.functional as F

from torch.distributions import Normal

import random

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

class ClippedCriticNet(nn.Module):

    def __init__(self, input_dim, output_dim, hidden_size):

        super().__init__()

        self.linear1 = nn.Linear(input_dim, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, output_dim)

        self.linear4 = nn.Linear(input_dim, hidden_size)
        self.linear5 = nn.Linear(hidden_size, hidden_size)
        self.linear6 = nn.Linear(hidden_size, output_dim)

    def forward(self, state, action):
        xu = torch.cat([state, action], 1)

        x1 = F.relu(self.linear1(xu))
        x1 = F.relu(self.linear2(x1))
        x1 = self.linear3(x1)

        x2 = F.relu(self.linear4(xu))
        x2 = F.relu(self.linear5(x2))
        x2 = self.linear6(x2)

        return x1, x2

class SoftActorNet(nn.Module):

    def __init__(self, input_dim, output_dim, hidden_size, action_scale):

        super().__init__()

        self.LOG_SIG_MAX = 2
        self.LOG_SIG_MIN = -20
        self.epsilon = 1e-6

        self.linear1 = nn.Linear(input_dim, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)

        self.mean_linear = nn.Linear(hidden_size, output_dim)
        self.log_std_linear = nn.Linear(hidden_size, output_dim)

        self.action_scale = torch.tensor(action_scale)
        self.action_bias = torch.tensor(0.)

    def forward(self, state):
        x = F.relu(self.linear1(state))
        x = F.relu(self.linear2(x))
        mean = self.mean_linear(x)
        log_std = self.log_std_linear(x)
        log_std = torch.clamp(log_std, min=self.LOG_SIG_MIN, max=self.LOG_SIG_MAX)
        return mean, log_std

    def sample(self, state):
        mean, log_std = self.forward(state)
        std = log_std.exp()
        normal = Normal(mean, std)
        x_t = normal.rsample()
        y_t = torch.tanh(x_t)
        action = y_t * self.action_scale + self.action_bias
        log_prob = normal.log_prob(x_t)
        log_prob -= torch.log(self.action_scale * (1 - y_t.pow(2)) + self.epsilon)
        log_prob = log_prob.sum(1, keepdim=True)
        mean = torch.tanh(mean) * self.action_scale + self.action_bias
        return action, log_prob, mean

    def to(self, device):
        self.action_scale = self.action_scale.to(device)
        self.action_bias = self.action_bias.to(device)
        return super().to(device)

class SoftActorCriticModel(object):

    def __init__(self, state_dim, action_dim, action_scale, args, device):

        self.gamma = args['gamma']
        self.tau = args['tau']
        self.alpha = args['alpha']
        self.device = device
        self.target_update_interval = args['target_update_interval']

        self.actor_net = SoftActorNet(
            input_dim=state_dim, output_dim=action_dim, hidden_size=args['hidden_size'], action_scale=action_scale
        ).to(self.device)
        self.critic_net = ClippedCriticNet(input_dim=state_dim + action_dim, output_dim=1, hidden_size=args['hidden_size']).to(device=self.device)
        self.critic_net_target = ClippedCriticNet(input_dim=state_dim + action_dim, output_dim=1, hidden_size=args['hidden_size']).to(self.device)

        hard_update(self.critic_net_target, self.critic_net)
        convert_network_grad_to_false(self.critic_net_target)

        self.actor_optim = torch.optim.Adam(self.actor_net.parameters())
        self.critic_optim = torch.optim.Adam(self.critic_net.parameters())

        self.target_entropy = -torch.prod(torch.Tensor(action_dim).to(self.device)).item()
        self.log_alpha = torch.zeros(1, requires_grad=True, device=self.device)
        self.alpha_optim = torch.optim.Adam([self.log_alpha])

    def select_action(self, state, evaluate=False):
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        if not evaluate:
            action, _, _ = self.actor_net.sample(state)
        else:
            _, _, action = self.actor_net.sample(state)
        return action.cpu().detach().numpy().reshape(-1)

    def update_parameters(self, memory, batch_size, updates):

        state_batch, action_batch, reward_batch, next_state_batch, mask_batch = memory.sample(batch_size=batch_size)

        state_batch = torch.FloatTensor(state_batch).to(self.device)
        next_state_batch = torch.FloatTensor(next_state_batch).to(self.device)
        action_batch = torch.FloatTensor(action_batch).to(self.device)
        reward_batch = torch.FloatTensor(reward_batch).unsqueeze(1).to(self.device)
        mask_batch = torch.FloatTensor(mask_batch).unsqueeze(1).to(self.device)

        with torch.no_grad():
            next_action, next_log_pi, _ = self.actor_net.sample(next_state_batch)
            next_q1_values_target, next_q2_values_target = self.critic_net_target(next_state_batch, next_action)
            next_q_values_target = torch.min(next_q1_values_target, next_q2_values_target) - self.alpha * next_log_pi
            next_q_values = reward_batch + mask_batch * self.gamma * next_q_values_target

        q1_values, q2_values = self.critic_net(state_batch, action_batch)
        critic1_loss = F.mse_loss(q1_values, next_q_values)
        critic2_loss = F.mse_loss(q2_values, next_q_values)
        critic_loss = critic1_loss + critic2_loss

        self.critic_optim.zero_grad()
        critic_loss.backward()
        self.critic_optim.step()

        action, log_pi, _ = self.actor_net.sample(state_batch)

        q1_values, q2_values = self.critic_net(state_batch, action)
        q_values = torch.min(q1_values, q2_values)

        actor_loss = ((self.alpha * log_pi) - q_values).mean()

        self.actor_optim.zero_grad()
        actor_loss.backward()
        self.actor_optim.step()

        alpha_loss = -(self.log_alpha * (log_pi + self.target_entropy).detach()).mean()

        self.alpha_optim.zero_grad()
        alpha_loss.backward()
        self.alpha_optim.step()

        self.alpha = self.log_alpha.exp()

        if updates % self.target_update_interval == 0:
            soft_update(self.critic_net_target, self.critic_net, self.tau)

        return critic_loss.item(), actor_loss.item()

def soft_update(target, source, tau):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)


def hard_update(target, source):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(param.data)


def convert_network_grad_to_false(network):
    for param in network.parameters():
        param.requires_grad = False

class ReplayMemory:

    def __init__(self, memory_size):
        self.memory_size = memory_size
        self.buffer = []
        self.position = 0

    def push(self, state, action, reward, next_state, mask):
        if len(self.buffer) < self.memory_size:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, mask)
        self.position = (self.position + 1) % self.memory_size

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done

    def __len__(self):
        return len(self.buffer)



def main():
    motions = ["ohuku", "curb", "zigzag", "ohukuRandom"]
    motion = motions[0]
    # motion = motions[1]
    # motion = motions[2]
    # motion = motions[3]

    if motion == "ohuku":
        cpu_log = "Cpu_0608_1646.csv"
        player_log = "Player_0608_1646.csv"
    elif motion == "curb":
        cpu_log = "Cpu_0613_2047.csv"
        player_log = "Player_0613_2047.csv"
    elif motion == "ohukuRandom":
        cpu_log = "Cpu_0608_1641.csv"
        player_log = "Player_0608_1641.csv"
    elif motion == "zigzag":
        cpu_log = "Cpu_0623_1312.csv"
        player_log = "Player_0623_1312.csv"

    delay = 0.2

    log_date = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    log_dir = f'/mnt/HDD/Photon_FPS/DRLModels/getAction/{motion}/{log_date}_different_send'

    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(level=20)

    # Set a random seed used in PFRL.
    utils.set_random_seed(0)

    n_dim_obs = 20
    n_actions = 9
    n_atoms = 51
    v_max = 10
    v_min = -10
    n_hidden_channels = 100
    n_hidden_layers = 3
    nonlinearity = F.relu
    last_wscale = 1.0
    
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
    pnn.to_factorized_noisy(act_q_func, sigma_scale=0.5)
    # Turn off explorer
    explorer = explorers.Greedy()

    act_opt = torch.optim.Adam(act_q_func.parameters(), 6.25e-5, eps=1.5 * 10 ** -4)

    # 学習用データ保存領域のサイズ
    capacity = 10**5
    betasteps = capacity - 1000 // 4

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

    args = {
        'gamma': 0.99,
        'tau': 0.005,
        'alpha': 0.2,
        'seed': 123456,
        'batch_size': 256,
        'hidden_size': 256,
        'start_steps': 1000,
        'updates_per_step': 1,
        'target_update_interval': 1,
        'memory_size': 100000,
        'epochs': 100,
        'eval_interval': 10
    }

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    action_space = Box(low=0.0, high=1.0, shape=(1,))
    action_size = action_space.low.size

    change_agent = SoftActorCriticModel(
        state_dim=n_dim_obs, action_dim = action_space.shape[0],
        action_scale = action_space.high[0], args=args, device=device
    )
    memory = ReplayMemory(args['memory_size'])

    n_input = 20
    episodes = 10001

    cpu_positions = {}
    cpu_velocity = {}
    cpu_keys = []

    # with open(f'/mnt/HDD/Photon_FPS/Log/Lag0/{motion}/{cpu_log}') as f:
    with open(f'../evaluate/EvaluateDiffLog/LagNone/{motion}/train/real_log_train.csv') as f:
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

    # with open(f'/mnt/HDD/Photon_FPS/Log/Lag0/{motion}/{player_log}') as f:
    with open(f'../evaluate/EvaluateDiffLog/LagNone/{motion}/train/delayed_log_train.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            row[0] = float(row[0])
            for k in range(1, 7):
                row[k] = float(row[k])
            player_positions[row[0]] = [row[1], row[2], row[3]]
            player_velocity[row[0]] = [row[4], row[5], row[6]]
            # time, x, z, y
            player_keys.append(row[0])

    action = 0

    player_length = len(player_keys)
    cpu_length = len(cpu_keys)

    for episode in range(episodes):
        # obs4steps = np.zeros((n_past, n_input), dtype=np.float32)
        obs = np.zeros(n_input, dtype=np.float32)
        action_R = 0
        change_R = 0
        max_R_action = 0
        max_R_change = 0

        last_position_x = np.zeros(4)
        last_position_y = np.zeros(4)
        last_velocity_x = np.zeros(4)
        last_velocity_y = np.zeros(4)
        last_time = np.zeros(4)

        cpu_index = 0

        for key in player_keys:
            action_reward = 0
            change_reward = 0
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

            if player_keys.index(key) < 4:
                continue
            else:
                obs = [last_time[0], last_position_x[0], last_position_y[0], last_velocity_x[0], last_velocity_y[0], last_time[1], last_position_x[1], last_position_y[1], last_velocity_x[1], last_velocity_y[1], last_time[2], last_position_x[2], last_position_y[2], last_velocity_x[2], last_velocity_y[2], last_time[3], last_position_x[3], last_position_y[3], last_velocity_x[3], last_velocity_y[3]]

                action = act_agent.act(obs)
                change_second = change_agent.select_action(obs)

                if len(memory) > args['batch_size']:
                    change_agent.update_parameters(memory, args['batch_size'], episode)

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
                        cpu_index -= 1
                        break

                if player_index >= player_length - 20 or cpu_index >= cpu_length - 20:
                    break
                
                for i in range(10):
                    actual_action = get_action_num(cpu_velocity[cpu_keys[last_cpu_index+i]][0], cpu_velocity[cpu_keys[last_cpu_index+i]][2])

                    pre_action = get_action_num(cpu_velocity[cpu_keys[last_cpu_index+i-1]][0], cpu_velocity[cpu_keys[last_cpu_index+i-1]][2])

                    if pre_action != actual_action:
                        actual_change_second = cpu_keys[last_cpu_index+i] - cpu_keys[last_cpu_index]
                        break
                    else:
                        actual_change_second = 0

                change_second = change_second * 0.2 # [0, 1] * 0.2 -> 0.2sまで
                change_reward = abs(actual_change_second - change_second)

                max_R_action += 1
                if actual_action == action:
                    action_reward = 1

                action_R += action_reward
                change_R -= change_reward

                done = False
                reset = False

                memory.push(state=obs, action=change_second, reward=change_reward, mask=float(not done))

                # change_agent.observe(obs, change_reward, done, reset)
                # change_agent.observe(torch.tensor(obs, dtype=float32), change_reward, done, reset)
                act_agent.observe(obs, action_reward, done, reset)

                with open(f'{log_dir}/check.csv', 'a') as f:
                    f.write(f'{episode}, {action}, {actual_action},{change_second}, {actual_change_second}, {action_reward}, {change_reward} \n')

        done = True
        reset = True

        change_agent.observe(obs, change_reward, done, reset)
        act_agent.observe(obs, action_reward, done, reset)

        print("Episode finished!")
        print("Episode: ", episode)
        print(f"total reward: {max_R_action}, {action_R}, {max_R_change}, {change_R}")
        print("=====================")

        with open(f'{log_dir}/result.csv', 'a') as f:
            f.write(f'{episode + 1}, {max_R_action}, {action_R}, {max_R_change}, {change_R}\n')

        if episode % 100 == 0 and episode > 2000:
            change_agent.save(f"{log_dir}/change_model{episode+1}")
            act_agent.save(f"{log_dir}/act_model{episode+1}")

if __name__ == "__main__":
    main()