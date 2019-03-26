import Bee_Files
import Helper
from random import random
from copy import deepcopy  # this import is actually really important due to the way pointers work in computer data
import pygame
import time
import statistics

TIME = True  # Whether to time the length of code running

if TIME:
    start_time = time.time()
else:
    start_time = 0

# Time step is assumed to be 20ms
REFRACTION = 40  # This is how long it takes for the bee to be able to be activated again, in time steps
ACTIVATION = 3   # This is how long a bee will be activated for in time steps
TOTAL_TIME = 60  # The number of time steps the simulation will run for; may need to be changed for slower waves
CHANCE_TO_BE_ACTIVATABLE = 0.58  # This is the probability that it is even possible to activate the bee
CHANCE_OF_SALTATORY_PROP = 0.001  # This is the probability that a bee activates in the far neighborhood
SAL_X_DIFF = 5  # The possible delta X between the wave and bee for Sal-Prop
SAL_Y_DIFF = 5  # The possible delta Y between the wave and bee for Sal-Prop
BEES_X_DIM = 101  # This is the size of the hive in the X direction, in number of bees
BEES_Y_DIM = 101  # This is the size of the hive in the Y direction, in number of bees
BEES_X_SIZE = 5  # The size of the Bee in the X direction
BEES_Y_SIZE = 5  # The size of the Bee in the Y direction
DISPLAY = True  # To display, or not to display?
PRINT_SPEED = True  # Whether to output the wave speed info to the console
SAVE_SPEEDS = True  # only works if PRINT_SPEED IS TRUE, saves a txt file with a list of all speeds, sorted

if DISPLAY:
    # Initialization of Drawing Stuffs(very professional vocabulary here)
    pygame.init()
    # This determines the dimensions of the hive Surface display
    surf = pygame.display.set_mode((BEES_X_DIM*BEES_X_SIZE, BEES_Y_DIM*BEES_Y_SIZE))
    pygame.display.set_caption("Shimmering Simulation")
else:
    surf = ""  # Placeholder to stop warnings

# generate the hive surface, creating a 2 dim "array", with the same dim as the screen
Hive = []
First_activations = []  # This records the time of first activation for a bee (excluding the generator)
for x in range(BEES_X_DIM):
    Bee_col = []
    Act_col = []
    for y in range(BEES_Y_DIM):
        Bee_col.append(Bee_Files.Bee(REFRACTION, ACTIVATION, random() < CHANCE_TO_BE_ACTIVATABLE))
        Act_col.append(-1)
    Hive.append(Bee_col)
    First_activations.append(Act_col)


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
                if not (Hive[col_ind][row_ind].get_has_activated() or # This should speed up the initial slow code part
                        Helper.dist(col_ind, row_ind, generator_location[0], generator_location[1],
                                    (BEES_X_DIM, BEES_Y_DIM))
                        > t*Helper.dist(SAL_X_DIFF, SAL_Y_DIFF, 0, 0, (BEES_X_DIM, BEES_Y_DIM))):
                    for mod_x_ind in range(len(relation_matrix)):
                        x_modifier = mod_x_ind - ((len(relation_matrix)-1)//2)
                        for mod_y_ind in range(len(relation_matrix[mod_x_ind])):
                            y_modifier = mod_y_ind - ((len(relation_matrix[mod_x_ind]) - 1) // 2)
                            if Last_Hive_State[(col_ind+x_modifier)
                                               % BEES_X_DIM][(row_ind+y_modifier) % BEES_Y_DIM].is_it_active():
                                Act_val += relation_matrix[mod_x_ind][mod_y_ind]
                    if Act_val < Threshold:  # only test if the bee will not otherwise activate
                        Test = False  # whether to check for sal-prop; only true if the wave is in the far neigh
                        for sal_X in range(SAL_X_DIFF):
                            for sal_Y in range(SAL_Y_DIFF):
                                if not Test:  # if this is true; why should we keep looking?
                                    # This check is manual because I'm too lazy rn to make clever code
                                    if Last_Hive_State[(col_ind + sal_X) % BEES_X_DIM][(row_ind + sal_Y)
                                                                                      % BEES_Y_DIM].is_it_active():
                                        Test = True
                                    elif Last_Hive_State[(col_ind - sal_X) % BEES_X_DIM][(row_ind + sal_Y)
                                                                                        % BEES_Y_DIM].is_it_active():
                                        Test = True
                                    elif Last_Hive_State[(col_ind + sal_X) % BEES_X_DIM][(row_ind - sal_Y)
                                                                                         % BEES_Y_DIM].is_it_active():
                                        Test = True
                                    elif Last_Hive_State[(col_ind - sal_X) % BEES_X_DIM][(row_ind - sal_Y)
                                                                                         % BEES_Y_DIM].is_it_active():
                                        Test = True
                        if Test:
                            if random() < CHANCE_OF_SALTATORY_PROP:
                                Act_val = Threshold

                    # If the bee receives enough of a signal it will be told to activate, else it will not be.
                if Act_val >= Threshold:
                    Hive[col_ind][row_ind].update_pulse(True)
                    First_activations[col_ind][row_ind] = t
                else:
                    Hive[col_ind][row_ind].update_pulse()
    # This simply updates the display window.
    if DISPLAY:
        Helper.print_hive(Hive, surf, (BEES_X_SIZE, BEES_Y_SIZE))  # runs the display

# This actually takes a comparably insignificant amount of time wrt the rest of the code
if PRINT_SPEED:  # Speed is topological distance per time step atm
    speeds = []  # A list of all speeds
    for x in range(len(First_activations)):
        for y in range(len(First_activations[x])):
            if First_activations[x][y] > -1:  # checks whether a valid time was recorded, to ignore
                speed = Helper.dist(x, y, generator_location[0],
                                    generator_location[1], (BEES_X_DIM, BEES_Y_DIM)) / First_activations[x][y]
                speeds.append(speed)
    mean_speed = statistics.mean(speeds)
    median_speed = statistics.median(speeds)
    max_speed = max(speeds)
    min_speed = min(speeds)

    print("Median speed: " + str(median_speed) + " distance / time step")
    print("Mean speed: " + str(mean_speed) + " distance / time step")
    print("Top speed: " + str(max_speed) + " distance / time step")
    print("Bottom speed: " + str(min_speed) + " distance / time step")
    if SAVE_SPEEDS:
        speeds.sort()
        with open('Speeds.txt', 'w') as f:  # change the string "Speeds.txt" to smt else if you want to make a diff file
            for item in speeds:
                f.write("%s\n" % item)

if TIME:
    print("--- %s seconds ---" % (time.time() - start_time))
