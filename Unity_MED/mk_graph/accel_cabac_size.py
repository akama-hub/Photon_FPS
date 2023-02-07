import numpy as np
import matplotlib.pyplot as plt
import csv


frame_delay = 3
steps = [-4, -3, -2, -1]

stepsize = np.zeros(4)
for i in range(4):
    stepsize[i] = 2 ** steps[i]
two_mlp_ohuku = [154.5, 137.8, 107.7, 88.8, 61.5, 35.5, 24.9, 14.7, 10.8, 7.9]
two_mlp_curb = [151, 135.4, 107, 88.3, 62.1, 36.6, 25.6, 15.6, 11.7, 8.6]
two_mlp_zigzag = [153.4, 137.1, 107.8, 88, 61.8, 37.2, 26.5, 16.6, 12.4, 9.1]


print("===========================")
print(f"making diff position png & eps graph")

delay = np.arange(1, 11)

p1 = plt.plot(stepsize, two_mlp_ohuku, linestyle="dotted", marker="o", color = "b")
p2 = plt.plot(stepsize, two_mlp_curb, linestyle="dashed", marker="o", color = "g")
p3 = plt.plot(stepsize, two_mlp_zigzag, linestyle="dashdot", marker="o", color = "r")

# plt.xlabel("delay[F] (20 ms/frame)")
plt.xlabel("stepsize")
plt.ylabel("data size [kB]")

plt.legend((p1[0], p2[0], p3[0]), ("Round-trip motion", "Circular motion", "Zigzag motion"), loc = 2, fontsize = 20)

# plt.savefig(f"./figure/ohuku/speed5_2action_ohuku.eps", bbox_inches='tight', pad_inches=0)
# plt.savefig(f"./figure/ohuku/speed5_2action_ohuku.png", bbox_inches='tight', pad_inches=0)
plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_size.eps", bbox_inches='tight', pad_inches=0)
plt.savefig(f"./figure/CABAC/{frame_delay}frame_cabac_size.png", bbox_inches='tight', pad_inches=0)
plt.clf()
plt.close()