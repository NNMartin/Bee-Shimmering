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


# Create new Figure and an Axes which fills it.
fig = plt.figure(figsize=(7, 7))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, 1), ax.set_xticks([])
ax.set_ylim(0, 1), ax.set_yticks([])

Hive = []
PlotHive = np.zeros(dimHive, dtype = [('position', float, 2), ('colour', float, 4)])

i = 0
for x in range(BEES_X_DIM):
    Bee_col = []
    for y in range(BEES_Y_DIM):
        xval = x / (BEES_X_DIM - 1)
        yval = y / (BEES_Y_DIM - 1)
        PlotHive[i][0] = [xval, yval]
        PlotHive[i][1] = wht
        Bee_col.append(Bee_Files.Bee(REFRACTION, ACTIVATION, random() < CHANCE_TO_BE_ACTIVATABLE))
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

# Construct the scatter which we will update during animation
scat = ax.scatter(PlotHive['position'][:, 0], PlotHive['position'][:, 1],
                  lw=0.5, edgecolors=PlotHive['colour'], facecolors='none')



# at the moment these numbers are just place holders for a PoC; must be odd by odd, though not necessarily rectangular.
relation_matrix = [[1/(68**(1/2)), 1/(29**(1/2)), 1/2, 1/(29**(1/2)), 1/(68**(1/2))],
                   [1/(26**(1/2)), 1, 1, 1, 1/(26**(1/2))], [1/5, 1, 0, 1, 1/5],
                   [1/(26**(1/2)), 1, 1, 1, 1/(26**(1/2))],
                   [1/(68**(1/2)), 1/(29**(1/2)), 1/2, 1/(29**(1/2)), 1/(68**(1/2))]]
# This is the threshold to which the bee needs to receive input before becoming active, Honestly probably should be
# replaced with something more complicated in the Bees at a later date
Threshold = 0.5



def update(frame_number):

    if frame_number == 0:  # This basically just makes sure that the generator bee activates
        Hive[generator_location[0]][generator_location[1]].activate()
    else:
        Last_Hive_State = deepcopy(Hive)  # To avoid object pointer issues we need to create a deep copy
        j = 0
        for col_ind in range(len(Hive)):
            for row_ind in range(len(Hive[col_ind])):
                # This is just the bees activation value, if it is equal or above threshold the bee will activate
                # Note that the way it is written it could theoretically be negative
                Act_val = 0
                # Here we start to extract the modifiers from the relationship matrix; then add them to the Act_val iff
                # the bee for which they function is active; note it makes the hive surface into a Torus because of the
                # %(modulus) in the if statement
                for mod_x_ind in range(len(relation_matrix)):
                    x_modifier = mod_x_ind - ((len(relation_matrix)-1)//2)
                    for mod_y_ind in range(len(relation_matrix[mod_x_ind])):
                        y_modifier = mod_y_ind - ((len(relation_matrix[mod_x_ind]) - 1) // 2)
                        if Last_Hive_State[(col_ind+x_modifier) % (BEES_X_DIM-1)][(row_ind+y_modifier) % (BEES_Y_DIM-1)].is_it_active():
                            Act_val += relation_matrix[mod_x_ind][mod_y_ind]
                # If the bee receives enough of a signal it will be told to activate, else it will not be.
                bee = Hive[col_ind][row_ind]
                if Act_val >= Threshold:
                    Hive[col_ind][row_ind].update_pulse(True)
                else:
                    Hive[col_ind][row_ind].update_pulse()
                if bee.is_active:
                    a = blk
                else:
                    a = wht
                PlotHive[j][1] = a
                j += 1

    # Update the scatter collection with the new colors.
    scat.set_edgecolors(PlotHive['colour'])




# Construct the animation, using the update function as the animation director.
animation = FuncAnimation(fig, update, interval=1)
plt.show()
