import numpy as np
import matplotlib.pyplot as plt
import csv

plt.rcParams["font.size"] = 20
# plt.rcParams["legend.labelspacing"] = 0
plt.rcParams["font.family"] = 'Times New Roman'
plt.figure(figsize = (8.0, 6.0))
markers = ["o", "v", "s", ">", "<"]
colors = ["r", "b", "g", "c", "m", "y", "k"]

marker_size = 12

# motion = "ohuku"
# motion = "curb"
# motion = "zigzag"

motions = ["ohuku", "curb", "zigzag"]

method = ["DR", "MAADR"]

for motion in motions:
    mlp_diff = []
    if motion == "ohuku":
        mlp_movement_file = '/mnt/HDD/akama/Unity/mlp/accel/ohuku/tp_xyv_xy/diff_result.csv'
        two_mlp_movement_file = '/mnt/HDD/akama/Unity/2mlp/accel/ohuku/TP_xyV_xy/9action/Accelevaluate/diff_result.csv'
        lr_movement_file = '/mnt/HDD/akama/Unity/LR-NLR/accel/ohuku/'
        dr_movement_file = f'/mnt/HDD/akama/Unity/DR-MAADR/{motion}/result.csv'

    elif motion == "curb":
        mlp_movement_file = '/mnt/HDD/akama/Unity/mlp/accel/curb/tp_xyv_xy/diff_result.csv'
        two_mlp_movement_file = '/mnt/HDD/akama/Unity/2mlp/accel/curb/TP_xyV_xy/AccelEvaluate/diff_result.csv'
        lr_movement_file = '/mnt/HDD/akama/Unity/LR-NLR/accel/curb/'
        dr_movement_file = f'/mnt/HDD/akama/Unity/DR-MAADR/{motion}/result.csv' 

    elif motion == "zigzag":
        mlp_movement_file = '/mnt/HDD/akama/Unity/mlp/accel/zigzag/tp_xyv_xy/diff_result.csv'
        two_mlp_movement_file = '/mnt/HDD/akama/Unity/2mlp/accel/zigzag/TP_xyV_xy/AccelEvaluate/diff_result.csv'
        lr_movement_file = '/mnt/HDD/akama/Unity/LR-NLR/accel/zigzag/'
        dr_movement_file = f'/mnt/HDD/akama/Unity/DR-MAADR/{motion}/result.csv'

    with open(mlp_movement_file) as f:
        reader = csv.reader(f)
        for row in reader:
            mlp_diff.append(float(row[3]))

    two_mlp_diff = []

    with open(two_mlp_movement_file) as f:
        reader = csv.reader(f)
        for row in reader:
            two_mlp_diff.append(float(row[6]))

    lr_diff = []
    nlr_diff = []
    for frame_delay in range(1, 11):
        with open(lr_movement_file + f'{frame_delay}frame/result.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                lr_diff.append(float(row[6].replace("[", "").replace("]", "")))
                nlr_diff.append(float(row[9]))

    delay_diff = []
    dr_diff = []
    maadr_diff = []
    with open(dr_movement_file) as f:
        reader = csv.reader(f)
        for row in reader:
            delay_diff.append(float(row[3]))
            dr_diff.append(float(row[6]))
            maadr_diff.append(float(row[9]))

    print("===========================")
    print(f"making diff position png & eps graph")

    print("MAADR: ", maadr_diff)
    print("2MLP: ", two_mlp_diff)

    decrese = (maadr_diff[9] - two_mlp_diff[9])/maadr_diff[9]

    print("Decrese Rate: ", decrese)

    delay = np.arange(1, 11)

    p1 = plt.plot(delay, delay_diff, linestyle = "--", dashes = (1, 1), marker=markers[0], color = colors[6], markerfacecolor = "None", ms = marker_size)
    p2 = plt.plot(delay, lr_diff, linestyle = "--", dashes = (2, 2), marker=markers[4], color = "orange", markerfacecolor = "None", ms = marker_size)
    p3 = plt.plot(delay, nlr_diff, linestyle = "--", dashes = (3, 3), marker='+', color = colors[3], markerfacecolor = "None", ms = marker_size)
    p4 = plt.plot(delay, dr_diff, linestyle = "--", dashes = (4, 4), marker='x', color = colors[2], markerfacecolor = "None", ms = marker_size)
    p5 = plt.plot(delay, maadr_diff, linestyle = "--", dashes = (5, 5), marker=markers[2], color = "grey", markerfacecolor = "None", ms = marker_size)
    p6 = plt.plot(delay, mlp_diff, linestyle = "--", dashes = (6, 6), marker=markers[3], color = colors[1], markerfacecolor = "None", ms = marker_size)
    p7 = plt.plot(delay, two_mlp_diff, linestyle = "--", dashes = (7, 7), marker='*', color = colors[0], markerfacecolor = "None", ms = marker_size)
    # p7 = plt.plot(delay, two_mlp_diff, linestyle = "--", dashes = (7, 7), marker='*', color = colors[0], markerfacecolor = "None", ms = marker_size, lw = 4)

    # plt.xlabel("delay[F] (20 ms/frame)")
    plt.xlabel("Delay [Frames]")
    plt.ylabel("Mean Euclidean Distance [m]")

    # plt.legend((p1[0], p4[0], p5[0], p6[0], p7[0]), ("NC", "DR [8]", "MAADR [9]", "MLP", "Proposed"), loc = 2)
    # plt.legend((p1[0], p4[0], p5[0], p6[0], p7[0]), ("NC", "DR [6]", "MAADR [7]", "MLP", "Proposed"), loc = 2)
    # plt.legend((p1[0], p4[0], p5[0], p6[0], p7[0]), ("NC", "DR [8]", "MAADR [9]", "MLP", "Proposed"), loc = 2, bbox_to_anchor=(-0.025, 0.535, 0.5, 0.5))
    plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0], p6[0], p7[0]), ("NC", "LR", "NLR", "DR", "MAADR", "MLP", "Proposed"), loc = 2)

    # plt.show()
    # plt.savefig(f"./figure/{motion}/accel_{motion}_DR.eps", bbox_inches='tight', pad_inches=0)
    # plt.savefig(f"./figure/{motion}/accel_{motion}_DR.png", bbox_inches='tight', pad_inches=0)

    # plt.savefig(f"./figure/{motion}/COG_accel_{motion}_DR.eps", bbox_inches='tight', pad_inches=0)
    # plt.savefig(f"./figure/{motion}/COG_accel_{motion}_DR.png", bbox_inches='tight', pad_inches=0)
    
    # plt.savefig(f"./figure/{motion}/COG_accel_{motion}_DR.eps", bbox_inches='tight', pad_inches=0)
    plt.savefig(f"./figure/{motion}/thesis23_accel_{motion}_DR.png", bbox_inches='tight', pad_inches=0)

    # plt.savefig(f"./figure/{motion}/syukatu_{motion}.eps", bbox_inches='tight', pad_inches=0)
    # plt.savefig(f"./figure/{motion}/syukatu_{motion}.png", bbox_inches='tight', pad_inches=0)

    # plt.savefig(f"./figure/{motion}/accel_{motion}_DR_LR.eps", bbox_inches='tight', pad_inches=0)
    # plt.savefig(f"./figure/{motion}/accel_{motion}_DR_LR.png", bbox_inches='tight', pad_inches=0)

    plt.clf()
    plt.close()