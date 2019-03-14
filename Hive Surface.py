import Bee_Files
import Helper
from random import random
from copy import deepcopy
import pygame


# Time step is assumed to be 20ms
REFRACTION = 40
ACTIVATION = 3
TOTAL_TIME = 65
CHANCE_TO_BE_ACTIVATABLE = 0.58
BEES_X_DIM = 100
BEES_Y_DIM = 100

# Initialization of Drawing Stuffs(very professional vocabulary here)
pygame.init()
surf = pygame.display.set_mode((BEES_X_DIM, BEES_Y_DIM))
pygame.display.set_caption("Shimmering Simulation")

# generate the hive surface
Hive = []
for x in range(BEES_X_DIM):
    Bee_col = []
    for y in range(BEES_Y_DIM):
        Bee_col.append(Bee_Files.Bee(REFRACTION, ACTIVATION, random() < CHANCE_TO_BE_ACTIVATABLE))
    Hive.append(Bee_col)

generator_location = (0, 0)
Hive[generator_location[0]][generator_location[1]] = Bee_Files.GeneratorBee(REFRACTION, ACTIVATION, True)

# at the moment these numbers are just place holders for a PoC; must be odd by odd, though not necessarily rectangular.
relation_matrix = [[0, 0.1, 0.25, 0.1, 0], [0.05, 0.15, 0.3, 0.15, 0.05], [0.2, 0.3, 0.6, 0.3, 0.2],
                   [0.2, 0.6, 0, 0.6, 0.2],  [0.2, 0.3, 0.6, 0.3, 0.2], [0.05, 0.15, 0.3, 0.15, 0.05],
                   [0, 0.1, 0.25, 0.1, 0]]
Threshold = 0.5


# actual simulation
for t in range(TOTAL_TIME):
    if t == 0:
        Hive[generator_location[0]][generator_location[1]].activate()
    else:
        Last_Hive_State = deepcopy(Hive)
        for col_ind in range(len(Hive)):
            for row_ind in range(len(Hive[col_ind])):
                Act_val = 0
                for mod_x_ind in range(len(relation_matrix)):
                    x_modifier = mod_x_ind - ((len(relation_matrix)-1)//2)
                    for mod_y_ind in range(len(relation_matrix[mod_x_ind])):
                        y_modifier = mod_y_ind - ((len(relation_matrix[mod_x_ind]) - 1) // 2)
                        if Last_Hive_State[(col_ind+x_modifier) % BEES_X_DIM][(row_ind+y_modifier) % BEES_Y_DIM].is_it_active():
                            Act_val += relation_matrix[mod_x_ind][mod_y_ind]
                if Act_val >= Threshold:
                    Hive[col_ind][row_ind].update_pulse(True)
                else:
                    Hive[col_ind][row_ind].update_pulse()
    Helper.print_hive(Hive, surf)  # Slightly better placeholder display
