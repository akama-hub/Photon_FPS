import numpy as np
import matplotlib.pyplot as plt
import csv

plt.rcParams["font.size"] = 20
plt.rcParams["font.family"] = 'Times New Roman'
plt.figure(figsize = (8.0, 6.0))
markers = ["o", "v", "s", ">", "<"]

frame_delay = 3

lr_diff = 0
with open(f"/mnt/HDD/akama/Unity/LR-NLR/accel/ohuku/{frame_delay}frame/result.csv") as f:
# with open(f"/mnt/HDD/akama/Unity/LR-NLR/accel/curb/{frame_delay}frame/result.csv") as f:
# with open(f"/mnt/HDD/akama/Unity/LR-NLR/accel/zigzag/{frame_delay}frame/result.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        lr_diff = float(row[6].replace("[", "").replace("]", ""))
        # nlr_diff.append(float(row[9]))

# steps = [-7.5, -7, -6, -5, -4, -3, -2.5, -2, -1.5, -1]
steps = [-4, -3, -2.5, -2, -1]
# steps = [-4, -3, -2, -1.5, -1]
# steps = [-4, -3, -2.5, -1.5, -1]

length = len(steps)

stepsize = np.zeros(length)

for i in range(length):
    stepsize[i] = 2 ** steps[i]

two_mlp_diff_ohuku = []
two_mlp_diff_curb = []
two_mlp_diff_zigzag = []

# ohuku_size = [154.5, 137.8, 107.7, 88.8, 61.5, 35.5, 24.9, 14.7, 10.8, 7.9]
# curb_size = [151, 135.4, 107, 88.3, 62.1, 36.6, 25.6, 15.6, 11.7, 8.6]
# zigzag_size = [153.4, 137.1, 107.8, 88, 61.8, 37.2, 26.5, 16.6, 12.4, 9.1]

ohuku_size = [61.5, 35.5, 24.9, 14.7, 7.9]
curb_size = [62.1, 36.6, 15.6, 11.7, 8.6]
zigzag_size = [61.8, 37.2, 26.5, 12.4, 9.1]

mlp_steps = [-1, -1.5, -2, -2.5, -3, -4, -5, -6, -7, -7.5, -10, -15, -20]
mlp_ohuku_size = [0.945, 1.564, 2.277, 2.972, 3.660, 5.192, 6.803, 8.447, 10.112, 10.930, 14.899, 22.898, 30.828, 52.2]
mlp_curb_size = [0.957, 1.6, 2.3, 3.0, 3.7, 5.2, 6.8, 8.5, 10.1, 10.9, 14.9, 22.9, 30.8, 52.2]
mlp_zigzag_size = [0.698,1.285, 2.014, 2.728, 3.421, 4.943,  6.518, 8.164, 9.829, 10.640, 14.591, 22.603, 30.532, 52.2]

mlp_diff_ohuku = [0.911576500150285, 0.1612089849503082, 0.198607633846993, 0.12057587124176013, 0.17686753832708701, 0.16120084835793191, 0.18194806945812184, 0.19075102300584318, 0.19138399284203164, 0.18597935275285563, 0.19003033145600592, 0.18638418807233414, 0.18866469508935899, 0.18758329790045]

mlp_diff_curb = []
with open(f"/mnt/HDD/akama/Unity/mlp/accel/curb/tp_xyv_xy/CABAC/diff_result.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        mlp_diff_curb.append(float(row[3].replace("[", "").replace("]", "")))

mlp_diff_curb.append(0.298536392039899)


mlp_diff_zigzag = [0.9774632557102589,0.6967114737238959,0.4820744617772629,0.34746421971014035,0.3646454581805259,0.30673454134352374,0.3057571905861589,0.29136271393868196,0.2842510940194544,0.28284796224636444,0.27921662920526225,0.2805881213484254,0.2802967692038631, 0.279270612142089]

for step in steps:
    with open(f'/mnt/HDD/akama/Unity/CABAC/2mlp/accel/ohuku/TP_xyV_xy/{frame_delay}frame_delay/{step}stepsize/diff_result.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            two_mlp_diff_ohuku.append(float(row[6]))

# for step in steps:
#     with open(f'/mnt/HDD/akama/Unity/CABAC/2mlp/accel/curb/TP_xyV_xy/{frame_delay}frame_delay/{step}stepsize/diff_result.csv') as f:
#         reader = csv.reader(f)
#         for row in reader:
#             two_mlp_diff_curb.append(float(row[6]))

# for step in steps:
#     with open(f'/mnt/HDD/akama/Unity/CABAC/2mlp/accel/zigzag/TP_xyV_xy/{frame_delay}frame_delay/{step}stepsize/diff_result.csv') as f:
#         reader = csv.reader(f)
#         for row in reader:
#             two_mlp_diff_zigzag.append(float(row[6]))


print("===========================")
print(f"making diff position png & eps graph")


p1 = plt.hlines(y = lr_diff, xmin=0, xmax=160, linestyle="dotted", color = "b")
p2 = plt.plot(ohuku_size, two_mlp_diff_ohuku, linestyle="solid", marker=markers[0], color = "r")
# p2 = plt.plot(curb_size, two_mlp_diff_curb, linestyle="solid", marker=markers[0], color = "r")
# p2 = plt.plot(zigzag_size, two_mlp_diff_zigzag, linestyle="solid", marker=markers[0], color = "r")
p3 = plt.plot(mlp_ohuku_size, mlp_diff_ohuku, linestyle="dashdot", marker=markers[1], color = "g")
# p3 = plt.plot(mlp_curb_size, mlp_diff_curb, linestyle="dashdot", marker=markers[1], color = "g")
# p3 = plt.plot(mlp_zigzag_size, mlp_diff_zigzag, linestyle="dashdot", marker=markers[1], color = "g")

plt.xlim(0, 65)
plt.ylim(0, 0.5)

# plt.xlabel("delay[F] (20 ms/frame)")
# plt.xlabel("stepsize")
plt.xlabel("data size [kB]")
plt.ylabel("Mean Euclidean Distance")

# plt.legend((p1, p2[0]), ("LR", "Proposed"), loc = 'upper right')
plt.legend((p1, p3[0], p2[0]), ("LR", "MLP", "Proposed"), loc = 'upper right')

plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_diff_size_ohuku.eps", bbox_inches='tight', pad_inches=0)
plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_diff_size_ohuku.png", bbox_inches='tight', pad_inches=0)

# plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_diff_size_curb.eps", bbox_inches='tight', pad_inches=0)
# plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_diff_size_curb.png", bbox_inches='tight', pad_inches=0)

# plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_diff_size_zigzag.eps", bbox_inches='tight', pad_inches=0)
# plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_diff_size_zigzag.png", bbox_inches='tight', pad_inches=0)

plt.show()

plt.clf()
plt.close()