import numpy as np
import matplotlib.pyplot as plt
import csv

mlp_lr_diff = []
mlp_nlr_diff = []

with open(f'/mnt/HDD/akama/Unity/2mlp/Fixed/zigzag/TP_xy/evaluate/diff_result.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        mlp_lr_diff.append(float(row[6]))
        mlp_nlr_diff.append(float(row[9]))


delay_diff = []
lr_diff = []
nlr_diff = []

for frame_delay in range(1, 11):
    # with open(f"/mnt/HDD/akama/Unity/LR-NLR/zigzag/speed5/{frame_delay}frame/result.csv") as f:
    with open(f"/mnt/HDD/akama/Unity/LR-NLR/zigzag/{frame_delay}frame/result.csv") as f:
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
p5 = plt.plot(delay, mlp_lr_diff, linestyle="solid", marker="o", color = "y")
p6 = plt.plot(delay, mlp_nlr_diff, linestyle="solid", marker="o", color = "r")

# plt.xlabel("delay[F] (20 ms/frame)")
plt.xlabel("delay")
plt.ylabel("Mean Euclidean Distance")

# plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0], p6[0], p7[0]), ("NC", "LR", "NLR", "MLP", "2MLP", "2MLP-LR", "2MLP-NLR"), loc = 2)
plt.legend((p1[0], p2[0], p3[0], p5[0], p6[0]), ("NC", "LR", "NLR", "2MLP-LR", "2MLP-NLR"), loc = 2)

plt.savefig(f"./figure/zigzag/zigzag.eps", bbox_inches='tight', pad_inches=0)
plt.savefig(f"./figure/zigzag/zigzag.png", bbox_inches='tight', pad_inches=0)
plt.clf()
plt.close()