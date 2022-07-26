from ast import arg
from distutils.log import Log
import socket
import signal
import os
from datetime import datetime
import csv
import string
import numpy as np
from sklearn.linear_model import LinearRegression #LinearRegression
import time 
import argparse

if __name__ == '__main__' :
    # ctrl-Cがなかなか反応しないのを直す
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    parser = argparse.ArgumentParser()
    parser.add_argument("-sp", "--servport", type=int)
    parser.add_argument("-up", "--unityport", type=int)
    parser.add_argument("-m", "--motion", type=str)
    parser.add_argument("-s", "--scheme", type=str)
    parser.add_argument("-l", "--latency", type=int)
    args = parser.parse_args()    # 4. 引数を解析

    # motion = "ohuku"
    # motion = "ohukuRandom"
    # motion = "zigzag"

    # log_dir = f'../Log/Lag{args.latency}/{motion}'
    # os.makedirs(log_dir, exist_ok=True)
    # evaluate_dir = f"evaluate/EvaluateDiffLog/Fixed30FPS/Lag{args.latency}/{args.motion}/{args.scheme}"
    # os.makedirs(evaluate_dir, exist_ok=True)
    train_dir = f'train_data/Fixed30FPS_SendRate60/Lag{args.latency}/{args.motion}'
    os.makedirs(train_dir, exist_ok=True)
    

    # log_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    # windowsでは:をファイル名につけてはいけない？？
    log_date = datetime.now().strftime("%m%d_%H%M")

    M_SIZE = 1024
    host = '127.0.0.1' 
    # 自分を指定
    # serv_port = 50010
    # unity_port = 50011
    # serv_port = 50000
    # unity_port = 50001

    # serv_port = 50020
    # unity_port = 50024
    # serv_port = 50030
    # unity_port = 50031

    serv_port = args.servport
    unity_port = args.unityport
    serv = (host, serv_port)
    unity_addr = (host, unity_port)
    cli_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    cli_sock.bind(serv)
    unity_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)

    turminal = ""
    if unity_port == 50001 or unity_port == 50024:
        turminal = "Real"
    elif unity_port == 50011 or unity_port == 50031:
        turminal = "Predict"
    elif unity_port == 50021:
        turminal = "Delayed"

    pos_x = np.array([])
    pos_y = np.array([])
    vel_x = np.array([])
    vel_y = np.array([])
    t = np.array([])

    print("connecting")

    while True:
        try:

            cli_data, cli_addr = cli_sock.recvfrom(M_SIZE)
            print("recieving data: ", cli_data)

            # now_dt = datetime.now()
            # nowTime = now_dt.minute * 60 + now_dt.second + now_dt.microsecond/1000000
            # print("Python now: ", nowTime)
            # clidata = time00000000x00000000y00000000z00000000
            #　負の値を取るとーも一文字になるので注意

            cli_str_data = cli_data.decode("utf-8")
            rcv_data = cli_str_data.split(',')

            # now_dt = datetime.now()
            # nowTime = now_dt.minute * 60 + now_dt.second + now_dt.microsecond/1000000
            # print("Python now: ", nowTime)
            # print("unity now: ", send_time)
            # print("time to Send Python from Unity: ", nowTime - float(send_time))

            with open(f'{train_dir}/{turminal}_log.csv', 'a') as f:
                writer = csv.writer(f, lineterminator='\n')
                # writer.writerow([float(rcv_data[i]) for i in range(1, len(rcv_data))])
                writer.writerow(rcv_data)
    
        except KeyboardInterrupt:
            print ('\n . . .\n')
            cli_sock.close()
            unity_sock.close()