import numpy as np
import matplotlib.pyplot as plt
import csv

plt.rcParams["font.size"] = 20
plt.rcParams["font.family"] = 'Times New Roman'
plt.figure(figsize = (8.0, 6.0))
markers = ["o", "v", "s", ">", "<"]

mlp_diff = []

with open(f'/mnt/HDD/akama/Unity/mlp/accel/curb/tp_xyv_xy/diff_result.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        mlp_diff.append(float(row[3]))

two_mlp_diff = []

with open(f'/mnt/HDD/akama/Unity/2mlp/accel/curb/TP_xyV_xy/AccelEvaluate/diff_result.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        two_mlp_diff.append(float(row[6]))

delay_diff = []
lr_diff = []
nlr_diff = []

for frame_delay in range(1, 11):
    with open(f"/mnt/HDD/akama/Unity/LR-NLR/accel/curb/{frame_delay}frame/result.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            delay_diff.append(float(row[3]))
            lr_diff.append(float(row[6].replace("[", "").replace("]", "")))
            nlr_diff.append(float(row[9]))

print("===========================")
print(f"making diff position png & eps graph")

delay = np.arange(1, 11)

p1 = plt.plot(delay, delay_diff, linestyle="dotted", marker=markers[0], color = "k")
p2 = plt.plot(delay, lr_diff, linestyle="dashed", marker=markers[1], color = "g")
p3 = plt.plot(delay, nlr_diff, linestyle="dashed", marker=markers[2], color = "y")
p4 = plt.plot(delay, mlp_diff, linestyle="dashdot", marker=markers[3], color = "b")
p5 = plt.plot(delay, two_mlp_diff, linestyle="solid", marker=markers[4], color = "r")

# plt.xlabel("delay[F] (20 ms/frame)")
plt.xlabel("delay")
plt.ylabel("Mean Euclidean Distance")

plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0]), ("NC", "LR", "NLR", "MLP", "Proposed"), loc = 2)

plt.savefig(f"./figure/curb/accel_curb.eps", bbox_inches='tight', pad_inches=0)
plt.savefig(f"./figure/curb/accel_curb.png", bbox_inches='tight', pad_inches=0)
plt.clf()
plt.close()