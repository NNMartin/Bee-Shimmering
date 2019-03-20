import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import Bee_Files
import Helper
from random import random
from copy import deepcopy

# Time step is assumed to be 20ms
REFRACTION = 40  # This is how long it takes for the bee to be able to be activated again, in time steps
ACTIVATION = 3   # This is how long a bee will be activated for in time steps
TOTAL_TIME = 30  # The number of time steps the simulation will run for; may need to be changed for slower waves
CHANCE_TO_BE_ACTIVATABLE = 0.58  # This is the probability that it is even possible to activate the bee
BEES_X_DIM = 101  # This is the size of the hive in the X direction, in number of bees
BEES_Y_DIM = 101  # This is the size of the hive in the Y direction, in number of bees
BEES_X_SIZE = 1  # The size of the Bee in the X direction
BEES_Y_SIZE = 3  # The size of the Bee in the Y direction
TSLAP = REFRACTION + ACTIVATION # Time since last activation pulse
dimHive = BEES_X_DIM * BEES_Y_DIM
wht = (0, 0, 0, 0)
blk = (0, 0, 0, 1)

Hive = []
PlotHive = np.zeros(dimHive, dtype = [('position', float, 2), ('colour', float, 4)])
HiveToHiveMap = {}
i = 0
for x in range(BEES_X_DIM):
    Bee_col = []
    for y in range(BEES_Y_DIM):
        xval = x / (BEES_X_DIM - 1)
        yval = y / (BEES_Y_DIM - 1)
        PlotHive[i][0] = [xval, yval]
        PlotHive[i][1] = wht
        Bee_col.append(Bee_Files.Bee(REFRACTION, ACTIVATION, random() < CHANCE_TO_BE_ACTIVATABLE))
        HiveToHiveMap[(x,y)] = i
        i += 1
    Hive.append(Bee_col)

# This creates the generator bee; to be frank this could also have been done with a bit more elegance, but it was
# creating a few to many bugs in the first version of the code; so I made it manual, it's a quick fix to make this work
# for multiple generator bees; if you can't do it just let me know and I'll write a patch
generator_location = (50, 50)
Hive[generator_location[0]][generator_location[1]] = Bee_Files.GeneratorBee(REFRACTION, ACTIVATION, True)
mid = (BEES_X_DIM - 1) * (BEES_Y_DIM - 1) / 2
PlotHive[int(round(mid, 0))][0] = [0.5, 0.5]
PlotHive[int(round(mid, 0))][1] = blk
