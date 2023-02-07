import numpy as np
import matplotlib.pyplot as plt
import csv

plt.rcParams["font.size"] = 20
plt.rcParams["font.family"] = 'Times New Roman'
plt.figure(figsize = (8.0, 6.0))
markers = ["o", "v", "s", ">", "<", "*", "x"]
colors = ["r", "b", "g", "c", "m", "y", "k"]

marker_size = 12

frame_delay = 3

# motion = "ohuku"
motion = "curb"
# motion = "zigzag"

# steps = [-7.5, -7, -6, -5, -4, -3, -2.5, -2, -1.5, -1]

method = ["DR", "MAADR"]

mlp_diff = []
if motion == "ohuku":
    mlp_movement_file = '/mnt/HDD/akama/Unity/mlp/accel/ohuku/tp_xyv_xy/diff_result.csv'
    two_mlp_movement_file = '/mnt/HDD/akama/Unity/CABAC/2mlp/accel/ohuku/TP_xyV_xy/'
    lr_movement_file = '/mnt/HDD/akama/Unity/LR-NLR/accel/ohuku/'
    dr_movement_file = f'/mnt/HDD/akama/Unity/DR-MAADR/{motion}/result.csv'
    steps = [-4, -3, -2.5, -2, -1]
    size = [61.5, 35.5, 24.9, 14.7, 7.9]
    mlp_size = [0.945, 1.564, 2.277, 2.972, 3.660, 5.192, 6.803, 8.447, 10.112, 10.930, 14.899, 22.898, 30.828, 52.2]
    mlp_diff = [0.911576500150285, 0.1612089849503082, 0.198607633846993, 0.12057587124176013, 0.17686753832708701, 0.16120084835793191, 0.18194806945812184, 0.19075102300584318, 0.19138399284203164, 0.18597935275285563, 0.19003033145600592, 0.18638418807233414, 0.18866469508935899, 0.18758329790045]

elif motion == "curb":
    mlp_movement_file = '/mnt/HDD/akama/Unity/mlp/accel/curb/tp_xyv_xy/diff_result.csv'
    two_mlp_movement_file = '/mnt/HDD/akama/Unity/CABAC/2mlp/accel/curb/TP_xyV_xy/'
    lr_movement_file = '/mnt/HDD/akama/Unity/LR-NLR/accel/curb/'
    dr_movement_file = f'/mnt/HDD/akama/Unity/DR-MAADR/{motion}/result.csv' 
    steps = [-4, -3, -2, -1.5, -1]
    size = [62.1, 36.6, 15.6, 11.7, 8.6]
    mlp_size = [0.957, 1.6, 2.3, 3.0, 3.7, 5.2, 6.8, 8.5, 10.1, 10.9, 14.9, 22.9, 30.8, 52.2]

    mlp_diff = []
    with open(f"/mnt/HDD/akama/Unity/mlp/accel/curb/tp_xyv_xy/CABAC/diff_result.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            mlp_diff.append(float(row[3].replace("[", "").replace("]", "")))

    mlp_diff.append(0.298536392039899)

elif motion == "zigzag":
    mlp_movement_file = '/mnt/HDD/akama/Unity/mlp/accel/zigzag/tp_xyv_xy/diff_result.csv'
    two_mlp_movement_file = '/mnt/HDD/akama/Unity/CABAC/2mlp/accel/zigzag/TP_xyV_xy/'
    lr_movement_file = '/mnt/HDD/akama/Unity/LR-NLR/accel/zigzag/'
    dr_movement_file = f'/mnt/HDD/akama/Unity/DR-MAADR/{motion}/result.csv'
    steps = [-4, -3, -2.5, -1.5, -1]
    size = [61.8, 37.2, 26.5, 12.4, 9.1]
    mlp_size = [0.698,1.285, 2.014, 2.728, 3.421, 4.943, 6.518, 8.164, 9.829, 10.640, 14.591, 22.603, 30.532, 52.2]
    mlp_diff = [0.9774632557102589,0.6967114737238959,0.4820744617772629,0.34746421971014035,0.3646454581805259,0.30673454134352374,0.3057571905861589,0.29136271393868196,0.2842510940194544,0.28284796224636444,0.27921662920526225,0.2805881213484254,0.2802967692038631, 0.279270612142089]

length = len(steps)
stepsize = np.zeros(length)

mlp_steps = [-1, -1.5, -2, -2.5, -3, -4, -5, -6, -7, -7.5, -10, -15, -20]

for i in range(length):
    stepsize[i] = 2 ** steps[i]

two_mlp_diff = []

for step in steps:
    with open(two_mlp_movement_file + f'{frame_delay}frame_delay/{step}stepsize/diff_result.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            two_mlp_diff.append(float(row[6]))

lr_diff = 0
with open(lr_movement_file + f'{frame_delay}frame/result.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        lr_diff = float(row[6].replace("[", "").replace("]", ""))

maadr_diff = []
with open(dr_movement_file) as f:
    reader = csv.reader(f)
    for row in reader:
        maadr_diff.append(float(row[9]))

maadr = maadr_diff[frame_delay-1]

print("===========================")
print(f"making diff position png & eps graph")

delay = np.arange(1, 11)

p1 = plt.hlines(y = lr_diff, xmin=0, xmax=70, color = colors[2])
p2 = plt.hlines(y = maadr, xmin=0, xmax=70, color = colors[1])
p3 = plt.plot(mlp_size, mlp_diff, linestyle = "--", dashes = (6, 6), marker="x", color = "orange", markerfacecolor = "None", ms = marker_size)
p4 = plt.plot(size, two_mlp_diff, linestyle = "--", dashes = (7, 7), marker="*", color = colors[0], markerfacecolor = "None", ms = marker_size)

plt.xlim(0, 65)
plt.ylim(0, 0.5)

# plt.xlabel("delay[F] (20 ms/frame)")
# plt.xlabel("stepsize")
plt.xlabel("data size [kB]")
plt.ylabel("Mean Euclidean Distance")

print("===============================")
print("frame delay ", frame_delay, " [F]")
print("Motion: ", motion)

# plt.legend((p1[0], p4[0], p5[0], p6[0], p7[0]), ("NC", "DR", "MAADR", "MLP", "Proposed"), loc = 2)
plt.legend((p1, p2, p3[0], p4[0]), ("LR", "MAADR", "MLP", "Proposed"), loc = 'upper right')

# plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_diff_size_{motion}_DR.eps", bbox_inches='tight', pad_inches=0)
# plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_diff_size_{motion}_DR.png", bbox_inches='tight', pad_inches=0)

# plt.savefig(f"./figure/CABAC/report_{frame_delay}frame_cabac_diff_size_{motion}_DR.eps", bbox_inches='tight', pad_inches=0)
plt.savefig(f"./figure/CABAC/report_{frame_delay}frame_cabac_diff_size_{motion}_DR.png", bbox_inches='tight', pad_inches=0)

plt.clf()
plt.close()