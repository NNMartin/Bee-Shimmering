import Bee_Files
import Helper
from random import random
from copy import deepcopy  # this import is actually really important due to the way pointers work in computer data
import pygame


# Time step is assumed to be 20ms
REFRACTION = 40  # This is how long it takes for the bee to be able to be activated again, in time steps
ACTIVATION = 3   # This is how long a bee will be activated for in time steps
TOTAL_TIME = 30  # The number of time steps the simulation will run for; may need to be changed for slower waves
CHANCE_TO_BE_ACTIVATABLE = 0.58  # This is the probability that it is even possible to activate the bee
BEES_X_DIM = 101  # This is the size of the hive in the X direction, in number of bees
BEES_Y_DIM = 101  # This is the size of the hive in the Y direction, in number of bees
BEES_X_SIZE = 1  # The size of the Bee in the X direction
BEES_Y_SIZE = 3  # The size of the Bee in the Y direction

# Initialization of Drawing Stuffs(very professional vocabulary here)
pygame.init()
# This determines the dimensions of the hive Surface display
surf = pygame.display.set_mode((BEES_X_DIM*BEES_X_SIZE, BEES_Y_DIM*BEES_Y_SIZE))
pygame.display.set_caption("Shimmering Simulation")

# generate the hive surface, creating a 2 dim "array", with the same dim as the screen
Hive = []
for x in range(BEES_X_DIM):
    Bee_col = []
    for y in range(BEES_Y_DIM):
        Bee_col.append(Bee_Files.Bee(REFRACTION, ACTIVATION, random() < CHANCE_TO_BE_ACTIVATABLE))
    Hive.append(Bee_col)

# This creates the generator bee; to be frank this could also have been done with a bit more elegance, but it was
# creating a few to many bugs in the first version of the code; so I made it manual, it's a quick fix to make this work
# for multiple generator bees; if you can't do it just let me know and I'll write a patch
generator_location = (50, 50)
Hive[generator_location[0]][generator_location[1]] = Bee_Files.GeneratorBee(REFRACTION, ACTIVATION, True)

# at the moment these numbers are just place holders for a PoC; must be odd by odd, though not necessarily rectangular.
relation_matrix = [[1/(68**(1/2)), 1/(29**(1/2)), 1/2, 1/(29**(1/2)), 1/(68**(1/2))],
                   [1/(26**(1/2)), 1, 1, 1, 1/(26**(1/2))], [1/5, 1, 0, 1, 1/5],
                   [1/(26**(1/2)), 1, 1, 1, 1/(26**(1/2))],
                   [1/(68**(1/2)), 1/(29**(1/2)), 1/2, 1/(29**(1/2)), 1/(68**(1/2))]]
# This is the threshold to which the bee needs to receive input before becoming active, Honestly probably should be
# replaced with something more complicated in the Bees at a later date
Threshold = 0.5


# actual simulation; this is just a loop that runs for a certain number of iterations
for t in range(TOTAL_TIME):
    if t == 0:  # This basically just makes sure that the generator bee activates
        Hive[generator_location[0]][generator_location[1]].activate()
    else:  # This is what the the actual iteration does
        Last_Hive_State = deepcopy(Hive)  # To avoid object pointer issues we need to create a deep copy
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
                        if Last_Hive_State[(col_ind+x_modifier) % BEES_X_DIM][(row_ind+y_modifier) % BEES_Y_DIM].is_it_active():
                            Act_val += relation_matrix[mod_x_ind][mod_y_ind]
                # If the bee receives enough of a signal it will be told to activate, else it will not be.
                if Act_val >= Threshold:
                    Hive[col_ind][row_ind].update_pulse(True)
                else:
                    Hive[col_ind][row_ind].update_pulse()
    # This simply updates the display window.
    Helper.print_hive(Hive, surf, (BEES_X_SIZE, BEES_Y_SIZE))  # Slightly better placeholder display
