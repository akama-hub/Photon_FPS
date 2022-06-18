import csv
import numpy as np
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-l", type=int)

args = parser.parse_args()

motions = ["ohuku", "curb", "zigzag", "ohukuRandom"]
motion = motions[0]
# motion = motions[1]
# motion = motions[3]

evaluate_dir = f"{motion}"

lag = np.array([])
with open(f'{evaluate_dir}/check_lag{args.l}.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        lag = np.append(lag, float(row[0]))

avg = np.average(lag)
var = np.var(lag)

print("Average: ", avg)
print("Variance: ", var)