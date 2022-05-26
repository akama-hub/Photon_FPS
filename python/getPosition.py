import socket
import signal
# import os
# from datetime import datetime
# import csv
from turtle import pos
import numpy as np
from sklearn.linear_model import LinearRegression #LinearRegression
import time 


# log_date = datetime.now().strftime("%Y%m%d-%H:%M:%S")
# # log_dir = f'/mnt/HDD/akama/Unity/movement_data/accel/ohuku'
# log_dir = f'/mnt/HDD/akama/Unity/movement_data/accel/zigzag'
# os.makedirs(log_dir, exist_ok=True)

# unity の速度はm/s

def linear_regression(pos_x, pos_y, t, delay):
    lr = LinearRegression()

    T = t.reshape(-1,1)
    X = pos_x.reshape(-1,1)
    Y = pos_y.reshape(-1,1)

    lr.fit(T, X)
    p_x = lr.coef_[0] * (t[3] + delay * (t[3] - t[2])) + lr.intercept_
    lr.fit(T, Y)
    p_y = lr.coef_[0] * (t[3] + delay * (t[3] - t[2])) + lr.intercept_

    return p_x, p_y

def nonlinear_regression(pos_x, pos_y, t, delay):
    T = t.reshape(-1,1).squeeze()
    X = pos_x.reshape(-1,1).squeeze()
    Y = pos_y.reshape(-1,1).squeeze()

    p_x = np.poly1d(np.polyfit(T, X, 2))(t[3] + delay * (t[3] - t[2]))
    p_y = np.poly1d(np.polyfit(T, Y, 2))(t[3] + delay * (t[3] - t[2]))

    return p_x, p_y

def DR(pos_x, pos_y, vel_x, vel_y, delay):
    predict_x = pos_x[3] + vel_x[3] * delay
    predict_y = pos_y[3] + vel_y[3] * delay
    
    return predict_x, predict_y

def MAADR(pos_x, pos_y, vel_x, vel_y, delay):
    predict_x = 0
    predict_y = 0

    accel_x = [vel_x[2] - vel_x[1], vel_x[3] - vel_x[2]]
    accel_y = [vel_y[2] - vel_y[1], vel_y[3] - vel_y[2]]

    if accel_x[1] == 0 and accel_y[1] == 0:
        predict_x = pos_x[3] + vel_x[3] * delay
        predict_y = pos_y[3] + vel_y[3] * delay
    elif accel_x[1] == accel_x[0] and accel_y[1] == accel_y[0]:
        predict_x = pos_x[3] + vel_x[3] * delay + accel_x[1] * (delay ** 2) / 2
        predict_y = pos_y[3] + vel_y[3] * delay + accel_y[1] * (delay ** 2) / 2
    else:
        np_velocity = np.array([vel_x[3], vel_y[3]])
        np_accelelation = np.array([accel_x[1], accel_y[1]])

        k = np.linalg.norm(np.cross(np_velocity, np_accelelation)) / (np.linalg.norm(np_velocity)**3)
        
        if k == 0:
            predict_x = pos_x[3] + vel_x[3] * delay + accel_x[1] * (delay ** 2) / 2
            predict_y = pos_y[3] + vel_y[3] * delay + accel_y[1] * (delay ** 2) / 2
        else:
            accel_x = k * (np.linalg.norm(np_velocity) ** 2) * (np_velocity[0] / np.linalg.norm(np_velocity))
            accel_y = k * (np.linalg.norm(np_velocity) ** 2) * (np_velocity[1] / np.linalg.norm(np_velocity))

            predict_x = pos_x[3] + vel_x[3] * delay + accel_x[1] * (delay ** 2) / 2
            predict_y = pos_y[3] + vel_y[3] * delay + accel_y[1] * (delay ** 2) / 2

    return predict_x, predict_y

if __name__ == '__main__' :
    # ctrl-Cがなかなか反応しないのを直す
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    M_SIZE = 1024
    host = '127.0.0.1' 
    # 自分を指定
    serv_port = 50000
    unity_port = 50001
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
    delay = 20 * 0.001
    # delay = (20 + (25*2)) * 0.001
    # delay = (20 + (50*2)) * 0.001

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
            # with open(f'{log_dir}/zigzag.csv', 'a') as f:
            #     writer = csv.writer(f, lineterminator='\n')
            #     writer.writerow([send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z])
            print(send_time, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z)
            # position_x = "00000020"
            
            if len(pos_x) < 4:
                pos_x = np.append(pos_x, float(position_x))
                pos_y = np.append(pos_y, float(position_y))
                vel_x = np.append(vel_x, float(velocity_x))
                vel_y = np.append(vel_y, float(velocity_y))
                t = np.append(t, float(send_time))

            else:
                pos_x[0] = float(position_x)
                pos_y[0] = float(position_y)
                vel_x[0] = float(velocity_x)
                vel_y[0] = float(velocity_y)
                t[0] = float(send_time)

                pos_x = np.roll(pos_x, -1)
                pos_y = np.roll(pos_y, -1)
                vel_x = np.roll(vel_x, -1)
                vel_y = np.roll(vel_y, -1)
                t = np.roll(t, -1)

                # p_x, p_y = linear_regression(pos_x, pos_y, t, delay)
                p_x, p_y = DR(pos_x, pos_y, vel_x, vel_y, delay)
                # p_x, p_y =  MAADR(pos_x, pos_y, vel_x, vel_y, delay)

                data = str(p_x) + "," + str(p_y) + "," + position_z
                print("send message: ", data)

                predict_data = data.encode("utf-8")
                print(predict_data)
                # print("Unity client", cli_data, data)
                print("Unity client", cli_data)
                unity_sock.sendto(predict_data, unity_addr)

                # end = time.time()
                # exe_time = end - start
                # print(start, end, exe_time) #0.003
    
        except KeyboardInterrupt:
            print ('\n . . .\n')
            cli_sock.close()
            unity_sock.close()