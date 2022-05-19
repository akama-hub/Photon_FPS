from ast import arg
from distutils.log import Log
import socket
import signal
import os
from datetime import datetime
import csv
from turtle import pos
import numpy as np
from sklearn.linear_model import LinearRegression #LinearRegression
import time 
import argparse

motion = "ohuku"
log_dir = f'../Log/{motion}'
os.makedirs(log_dir, exist_ok=True)

if __name__ == '__main__' :
    # ctrl-Cがなかなか反応しないのを直す
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    parser = argparse.ArgumentParser()
    parser.add_argument("-sp", "--sendport")
    parser.add_argument("-rp", "--recieveport")
    parser.add_argument("-l", "--latency")
    args = parser.parse_args()    # 4. 引数を解析

    log_date = datetime.now().strftime("%m%d-%H:%M")
    # # log_dir = f'/mnt/HDD/akama/Unity/movement_data/accel/ohuku'
    # log_dir = f'/mnt/HDD/akama/Unity/movement_data/accel/zigzag'

    M_SIZE = 1024
    host = '127.0.0.1' 
    # 自分を指定
    # serv_port = 50010
    # unity_port = 50011
    # serv_port = 50000
    # unity_port = 50001
    serv_port = args.recieveport
    unity_port = args.sendport
    serv = (host, serv_port)
    unity_addr = (host, unity_port)
    cli_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    cli_sock.bind(serv)
    unity_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)

    pos_x = np.array([])
    pos_y = np.array([])
    vel_x = np.array([])
    vel_y = np.array([])
    t = np.array([])

    # frame_delay = 1
    # delay = frame_delay * 0.02
    delay = 0.1

    print("connecting")

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

            print("recieving data: ", cli_data)
            for data in cli_str_data:
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

            with open(f'{log_dir}/{args.latency}_{log_date}.csv', 'a') as f:
                writer = csv.writer(f, lineterminator='\n')
                writer.writerow([send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z])
            print(send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z)

                # end = time.time()
                # exe_time = end - start
                # print(start, end, exe_time) #0.003
    
        except KeyboardInterrupt:
            print ('\n . . .\n')
            cli_sock.close()
            unity_sock.close()