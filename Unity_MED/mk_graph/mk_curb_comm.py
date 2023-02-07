import numpy as np
import matplotlib.pyplot as plt
import csv

digital_diff = []
analog_diff = []

for sn in range(0, 21, 5):
    diff_position = []
    with open(f'/mnt/HDD/akama/Unity/2mlp/curb/TP_xy/comm/speed5/digital/sn{sn}/diff_result.csv') as f:
        for row in reader:
            diff_position.append(float(row[6]))
        digital_diff.append(diff_position)

    diff_position = []
    with open(f'/mnt/HDD/akama/Unity/2mlp/curb/TP_xy/comm/speed5/analog/sn{sn}/diff_result.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            diff_position.append(float(row[6]))
        analog_diff.append(diff_position)

delay_diff = []
lr_diff = []
nlr_diff = []

for frame_delay in range(1, 11):
    with open(f"/mnt/HDD/akama/Unity/LR-NLR/curb/speed5/{frame_delay}frame/result.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            delay_diff.append(float(row[3]))
            lr_diff.append(float(row[6].replace("[", "").replace("]", "")))
            nlr_diff.append(float(row[9]))


for frame_delay in range(1, 11):
    print("===========================")
    print(f"making diff position png & eps graph when {frame_delay} [f] Delay")

    sn = np.arange(0, 21, 5)

    each_frame_delay_diff = np.array([delay_diff[frame_delay-1]]*5)
    each_frame_lr_diff = np.array([lr_diff[frame_delay-1]]*5)
    each_frame_nlr_diff = np.array([nlr_diff[frame_delay-1]]*5)
    
    DC = np.array([diff[frame_delay-1] for diff in digital_diff])
    AC = np.array([diff[frame_delay-1] for diff in analog_diff])

    print(DC, AC)

    p1 = plt.plot(sn, each_frame_delay_diff, linestyle="dotted", marker="o", color = "k")
    p2 = plt.plot(sn, each_frame_lr_diff, linestyle="dashdot", marker="o", color = "g")
    p3 = plt.plot(sn, each_frame_nlr_diff, linestyle="dashdot", marker="o", color = "c")
    p5 = plt.plot(sn, DC, linestyle="solid", marker="o", color = "y")
    p6 = plt.plot(sn, AC, linestyle="solid", marker="o", color = "r")

    # plt.xlabel("delay[F] (20 ms/frame)")
    plt.xlabel("SN")
    plt.ylabel("Mean Euclidean Distance")

    # plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0], p6[0], p7[0]), ("NC", "LR", "NLR", "MLP", "2MLP", "2MLP-LR", "2MLP-NLR"), loc = 2)
    plt.legend((p1[0], p2[0], p3[0], p5[0], p6[0]), ("NC", "LR", "NLR", "2MLP-DC", "2MLP-AC"), loc = 2)

    plt.savefig(f"./figure/curb/speed5_curb_comm_delay{frame_delay}F.eps", bbox_inches='tight', pad_inches=0)
    plt.savefig(f"./figure/curb/speed5_curb_comm_delay{frame_delay}F.png", bbox_inches='tight', pad_inches=0)
    plt.clf()
    plt.close()