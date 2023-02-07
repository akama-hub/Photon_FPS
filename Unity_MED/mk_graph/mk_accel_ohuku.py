import numpy as np
import matplotlib.pyplot as plt
import csv

NV_mlp_lr_diff = []
NV_mlp_nlr_diff = []

with open(f'/mnt/HDD/akama/Unity/2mlp/accel/ohuku/TP_xy/2action/evaluate/diff_result.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        NV_mlp_lr_diff.append(float(row[6]))
        NV_mlp_nlr_diff.append(float(row[9]))

V_mlp_lr_diff = []
V_mlp_nlr_diff = []

with open(f'/mnt/HDD/akama/Unity/2mlp/accel/ohuku/TP_xyV_xy/2action/evaluate/diff_result.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        V_mlp_lr_diff.append(float(row[6]))
        V_mlp_nlr_diff.append(float(row[9]))


delay_diff = []
lr_diff = []
nlr_diff = []

for frame_delay in range(1, 11):
    # with open(f"/mnt/HDD/akama/Unity/LR-NLR/ohuku/speed5/{frame_delay}frame/result.csv") as f:
    with open(f"/mnt/HDD/akama/Unity/LR-NLR/accel/ohuku/{frame_delay}frame/result.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            delay_diff.append(float(row[3]))
            lr_diff.append(float(row[6].replace("[", "").replace("]", "")))
            nlr_diff.append(float(row[9]))

print("===========================")
print(f"making diff position png & eps graph")

delay = np.arange(1, 11)

p1 = plt.plot(delay, delay_diff, linestyle="dotted", marker="o", color = "k")
p2 = plt.plot(delay, lr_diff, linestyle="dashdot", marker="o", color = "g")
p3 = plt.plot(delay, nlr_diff, linestyle="dashdot", marker="o", color = "c")
p5 = plt.plot(delay, NV_mlp_lr_diff, linestyle="solid", marker="o", color = "y")
p6 = plt.plot(delay, NV_mlp_nlr_diff, linestyle="solid", marker="o", color = "r")
p7 = plt.plot(delay, V_mlp_lr_diff, linestyle="dashed", marker="o", color = "purple")
p8 = plt.plot(delay, V_mlp_nlr_diff, linestyle="dashed", marker="o", color = "darkblue")

# plt.xlabel("delay[F] (20 ms/frame)")
plt.xlabel("delay")
plt.ylabel("Mean Euclidean Distance")

plt.legend((p1[0], p2[0], p3[0], p5[0], p6[0], p7[0], p8[0]), ("NC", "LR", "NLR", "TP_2MLP-LR", "TP_2MLP-NLR", "TPV_2MLP-LR", "TPV_2MLP-NLR"), loc = 2)

# plt.savefig(f"./figure/ohuku/speed5_2action_ohuku.eps", bbox_inches='tight', pad_inches=0)
# plt.savefig(f"./figure/ohuku/speed5_2action_ohuku.png", bbox_inches='tight', pad_inches=0)
plt.savefig(f"./figure/ohuku/accel_2action_ohuku.eps", bbox_inches='tight', pad_inches=0)
plt.savefig(f"./figure/ohuku/accel_2action_ohuku.png", bbox_inches='tight', pad_inches=0)
plt.clf()
plt.close()