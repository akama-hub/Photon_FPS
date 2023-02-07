import numpy as np
import matplotlib.pyplot as plt
import csv

plt.rcParams["font.size"] = 20
plt.rcParams["font.family"] = 'Times New Roman'
plt.figure(figsize = (8.0, 6.0))
markers = ["o", "v", "s", ">", "<", "*", "x"]
colors = ["r", "b", "g", "c", "m", "y", "k"]
x_max = 140
y_max = 0.8

marker_size = 12

# frame_delay = 9
frame_delays = [3, 6, 9]

# motion = "ohuku"
# motion = "curb"
# motion = "zigzag"

motions = ["ohuku", "curb", "zigzag"]

method = ["DR", "MAADR"]

# steps = [-1, -1.5, -2, -2.5, -3, -4, -5, -6, -7, -7.5]
# steps = [-1, -1.5, -2, -2.5, -2.6, -2.7, -2.8, -2.9, -3, -3.1, -3.2, -3.3, -3.4, -3.5, -3.6, -3.7, -3.8, -3.9, -4, -4.1, -4.2, -4.3, -4.4, -4.5, -4.6, -4.7, -4.8, -4.9, -5, -5.1, -5.2, -5.3, -5.4, -5.5, -5.6, -5.7, -5.8, -5.9, -6, -6.1, -6.2, -6.3, -6.4, -6.5, -6.6, -6.7, -6.8, -6.9, -7, -7.1, -7.2, -7.3, -7.4, -7.5, -7.6, -7.7, -7.8, -7.9]
# steps = [-1, -2, -3, -4, -5, -6, -7]

for motion in motions:
    mlp_default_diff = []
    mlp_default_size = 52.2

    lr_movement_file = f'/mnt/HDD/akama/Unity/LR-NLR/accel/{motion}/'

    with open(f'/mnt/HDD/akama/Unity/mlp/accel/{motion}/tp_xyv_xy/diff_result.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            mlp_default_diff.append(float(row[3]))

    for frame_delay in frame_delays:
        mlp_movement_file = f'/mnt/HDD/akama/Unity/mlp/accel/another-galleria/{frame_delay}frame_{motion}_mlp_cabac.csv'
        two_mlp_movement_file = f'/mnt/HDD/akama/Unity/CABAC/2mlp/accel/{motion}/TP_xyV_xy/'
        dr_movement_file = f'/mnt/HDD/akama/Unity/DR-MAADR/{motion}/result.csv'
        if motion == "ohuku":
            steps = [-1, -2, -3, -4, -6, -7]
             
        elif motion == "curb":
            steps = [-1, -2, -3, -4, -5, -6, -7]

        elif motion == "zigzag":
            steps = [-1, -2, -3, -4, -5, -6, -7]

        mlp_diff = []
        mlp_size = []
        mlp_hit = [-1, -4, -7, -10, -15, -20]
        with open(mlp_movement_file) as f:
            reader = csv.reader(f)
            for row in reader:
                if float(row[0]) in mlp_hit:
                    mlp_size.append(float(row[1])/1000)
                    mlp_diff.append(float(row[2]))

        mlp_diff.append(mlp_default_diff[frame_delay-1])
        mlp_size.append(mlp_default_size)
        

        two_mlp_diff = []
        size = {}
        size_key = []

        model_size_dir = f'/mnt/HDD/akama/Unity/CABAC/2mlp/accel/data_size/{motion}/{frame_delay}/data_size.csv'

        with open(model_size_dir) as f:
            reader = csv.reader(f)
            for row in reader:
                size[float(row[0])] = float(row[1])/1000 + float(row[2])/1000
                size_key.append(float(row[0]))

        two_mlp_size = []
        for key in size_key:
            if key in steps:
                two_mlp_size.append(size[key])
        

        for step in steps:
            with open(f'{two_mlp_movement_file}/{frame_delay}frame_delay/{step}stepsize/diff_result.csv') as f:
                reader = csv.reader(f)
                for row in reader:
                    two_mlp_diff.append(float(row[6]))


        dr_diff = []
        maadr_diff = []
        with open(dr_movement_file) as f:
            reader = csv.reader(f)
            for row in reader:
                dr_diff.append(float(row[6]))
                maadr_diff.append(float(row[9]))

        dr = dr_diff[frame_delay-1]
        maadr = maadr_diff[frame_delay-1]

        lr_diff = 0
        with open(lr_movement_file + f'{frame_delay}frame/result.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                lr_diff = float(row[6].replace("[", "").replace("]", ""))

        print("===========================")
        print(f"making diff position png & eps graph")

        print("frame delay ", frame_delay, " [F]")
        print("Motion: ", motion)

        delay = np.arange(1, 11)

        p1 = plt.hlines(y = lr_diff, xmin=0, xmax=x_max, color = colors[2])
        p2 = plt.hlines(y = maadr, xmin=0, xmax=x_max, color = "grey")
        p3 = plt.plot(mlp_size, mlp_diff, linestyle = "--", dashes = (6, 6), marker=markers[3], color = colors[1], markerfacecolor = "None", ms = marker_size)
        p4 = plt.plot(two_mlp_size, two_mlp_diff, linestyle = "--", dashes = (7, 7), marker='o', color = colors[0], markerfacecolor = "None", ms = marker_size)

        plt.xlim(0, x_max)
        plt.ylim(0, y_max)

        plt.xticks([0, 50, 100])
        plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8])

        # plt.xlabel("delay[F] (20 ms/frame)")
        # plt.xlabel("stepsize")
        plt.xlabel("Rate(Data Size) [KB]")
        plt.ylabel("Mean Euclidean Distance [m]")

        # plt.legend((p1[0], p4[0], p5[0], p6[0], p7[0]), ("NC", "DR", "MAADR", "MLP", "Proposed"), loc = 2)
        # plt.legend((p1, p2, p3[0], p4[0]), ("DR", "MAADR", "MLP", "Proposed"), loc = 'upper right')
        # plt.legend((p2, p3[0], p4[0]), ("MAADR [9]", "MLP", "Proposed"), loc = 'upper right')

        # plt.legend((p2, p3[0], p4[0]), ("MAADR [7]", "MLP", "Proposed"), loc = 'upper right')
        plt.legend((p1, p2, p3[0], p4[0]), ("LR", "MAADR", "MLP", "Proposed"), loc = 'upper right')

        # plt.savefig(f"./figure/CABAC/eps/{frame_delay}frame_cabac_diff_size_{motion}_DR.eps", bbox_inches='tight', pad_inches=0)
        # plt.savefig(f"./figure/CABAC/png/{frame_delay}frame_cabac_diff_size_{motion}_DR.png", bbox_inches='tight', pad_inches=0)

        # plt.savefig(f"./figure/CABAC/eps/int_{frame_delay}frame_cabac_diff_size_{motion}_DR.eps", bbox_inches='tight', pad_inches=0)
        # plt.savefig(f"./figure/CABAC/png/int_{frame_delay}frame_cabac_diff_size_{motion}_DR.png", bbox_inches='tight', pad_inches=0)

        # plt.savefig(f"./figure/CABAC/eps/COG_int_{frame_delay}frame_cabac_diff_size_{motion}_DR.eps", bbox_inches='tight', pad_inches=0)
        # plt.savefig(f"./figure/CABAC/png/COG_int_{frame_delay}frame_cabac_diff_size_{motion}_DR.png", bbox_inches='tight', pad_inches=0)

        plt.savefig(f"./figure/CABAC/png/report_int_{frame_delay}frame_cabac_diff_size_{motion}_DR.png", bbox_inches='tight', pad_inches=0)

        plt.clf()
        plt.close()