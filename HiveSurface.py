import Bee_Files
import Helper
from random import random
from copy import deepcopy  # this import is actually really important due to the way pointers work in computer data
import pygame
import time
import statistics
import numpy as np
from scipy import linalg as lin
from matplotlib import pyplot as plt

# setting a seed. We can change this later, but useful when running simulations
# for a single parameter.
np.random.seed(10)

def simulation(REFRACTION=40, ACTIVATION=3, TOTAL_TIME=60, Threshold=0.5,
                CHANCE_TO_BE_ACTIVATABLE=0.58, CHANCE_OF_SALTATORY_PROP=0.001,
                DISPLAY = False, TIME = True, plots=False, ret=False):
    """
    :param REFRACTION: how many ticks the bee must rest for between activations
    :param int ACTIVATION: how many ticks the bee will remain active for
    :param int TOTAL_TIME: The number of time steps the simulation will run for
    :param double Threshold: The threshold value needed to be reached for a bee to activate
    :param double CHANCE_TO_BE_ACTIVATABLE: The probability that it is even possible to activate the bee
    :param double CHANCE_OF_SALTATORY_PROP: This is the probability that a bee activates in the far neighborhood
    :param bool DISPLAY: Whether to show display or not
    :param bool TIME: Whether to time the length of code running
    :param bool plots: Whether to show the plots or not
    :param bool ret: whether or not to return simulation quantities

    :return list: Returns a list of quantities

    Time step is assumed to be 20ms. If <ret> is True, returns a list containing:
    wavespeed,
    """

    if TIME:
        start_time = time.time()
    else:
        start_time = 0

    ACTIVATION_MODE = 1 #1 = choose to activate on a per signal, 0 = choose to ignore all
    SAL_X_DIFF = 5.0  # The possible delta X between the wave and bee for Sal-Prop
    SAL_Y_DIFF = 5.0  # The possible delta Y between the wave and bee for Sal-Prop
    BEES_X_DIM = 100  # This is the size of the hive in the X direction, in number of bees
    BEES_Y_DIM = 100  # This is the size of the hive in the Y direction, in number of bees
    BEES_X_SIZE = 5.0  # The size of the Bee in the X direction
    BEES_Y_SIZE = 5.0  # The size of the Bee in the Y direction

    if DISPLAY:
        # Initialization of Drawing Stuffs(very professional vocabulary here)
        pygame.init()
        # This determines the dimensions of the hive Surface display
        surf = pygame.display.set_mode(((int)(BEES_X_DIM*BEES_X_SIZE), (int)(BEES_Y_DIM*BEES_Y_SIZE)))
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
            Bee_col.append(Bee_Files.Bee(REFRACTION, ACTIVATION, (1-ACTIVATION_MODE)*random() < CHANCE_TO_BE_ACTIVATABLE))
            Act_col.append(-1)
        Hive.append(Bee_col)
        First_activations.append(Act_col)


    # This creates the generator bee; to be frank this could also have been done with a bit more elegance, but it was
    # creating a few to many bugs in the first version of the code; so I made it manual, it's a quick fix to make this work
    # for multiple generator bees; if you can't do it just let me know and I'll write a patch
    generator_location = (0, 0)
    Hive[generator_location[0]][generator_location[1]] = Bee_Files.GeneratorBee(REFRACTION, ACTIVATION, True)

    # at the moment these numbers are just place holders for a PoC; must be odd by odd, though not necessarily rectangular.
    R = np.zeros([BEES_Y_DIM,BEES_X_DIM])

    R[BEES_Y_DIM-2,BEES_X_DIM-2]=   1/(68**(1/2))
    R[BEES_Y_DIM-2,BEES_X_DIM-1]=   1/(29**(1/2))
    R[BEES_Y_DIM-2,0]=              1/2
    R[BEES_Y_DIM-2,1]=              1/(29**(1/2))
    R[BEES_Y_DIM-2,2]=              1/(68**(1/2))

    R[BEES_Y_DIM-1,BEES_X_DIM-2]=   1/(26**(1/2))
    R[BEES_Y_DIM-1,BEES_X_DIM-1]=   1
    R[BEES_Y_DIM-1,0]=              1
    R[BEES_Y_DIM-1,1]=              1
    R[BEES_Y_DIM-1,2]=              1/(26**(1/2))

    R[0,BEES_X_DIM-1]=              1
    R[0,0]=                         0
    R[0,2]=                         1/5

    R[1,BEES_X_DIM-2]=              1/(26**(1/2))
    R[1,BEES_X_DIM-1]=              1
    R[1,0]=                         1
    R[1,1]=                         1
    R[1,2]=                         1/(26**(1/2))

    R[2,BEES_X_DIM-2]=              1/(68**(1/2))
    R[2,BEES_X_DIM-1]=              1/(29**(1/2))
    R[2,0]=                         1/2
    R[2,1]=                         1/(29**(1/2))
    R[2,2]=                         1/(68**(1/2))

    Y_dist=np.arange(BEES_Y_DIM)-(np.arange(BEES_Y_DIM)-BEES_Y_DIM/2.0)-np.abs(np.arange(BEES_Y_DIM)-BEES_Y_DIM/2.0)
    X_dist=np.arange(BEES_X_DIM)-(np.arange(BEES_X_DIM)-BEES_X_DIM/2.0)-np.abs(np.arange(BEES_X_DIM)-BEES_X_DIM/2.0)
    Y_dist_matrix = np.resize(np.tile(Y_dist,BEES_X_DIM),[BEES_X_DIM,BEES_Y_DIM])
    X_dist_matrix = np.transpose(np.resize(np.tile(X_dist,BEES_Y_DIM),[BEES_Y_DIM,BEES_X_DIM]))
    Dist_matrix=6*np.sqrt(Y_dist_matrix*Y_dist_matrix+(BEES_X_SIZE/BEES_Y_SIZE)**2*X_dist_matrix*X_dist_matrix)

    S=np.sqrt(Y_dist_matrix*Y_dist_matrix+(SAL_Y_DIFF/SAL_X_DIFF)**2*X_dist_matrix*X_dist_matrix)
    S=np.heaviside(SAL_Y_DIFF-S,0)


    # This is the threshold to which the bee needs to receive input before becoming active, Honestly probably should be
    # replaced with something more complicated in the Bees at a later date


    HIVE_STATE=np.zeros([TOTAL_TIME,BEES_X_DIM,BEES_Y_DIM])
    # actual simulation; this is just a loop that runs for a certain number of iterations
    for t in range(TOTAL_TIME):
        if t == 0:  # This basically just makes sure that the generator bee activates
            Hive[generator_location[0]][generator_location[1]].activate()
            HIVE_STATE[0]=np.zeros([BEES_X_DIM,BEES_Y_DIM])
            HIVE_STATE[0,generator_location[0],generator_location[1]]=1

        else:  # This is what the the actual iteration does
            HIVE_STATE_TEMP=np.copy(HIVE_STATE[t-1])
            HIVE_STATE_TEMP=np.real(np.fft.ifft2(np.fft.fft2(HIVE_STATE_TEMP)*np.fft.fft2(R)))
            HIVE_STATE_TEMP=np.heaviside(HIVE_STATE_TEMP/Threshold-1,1)
            if ACTIVATION_MODE==1:
                HIVE_STATE_TEMP=CHANCE_TO_BE_ACTIVATABLE*HIVE_STATE_TEMP\
                -np.resize(np.random.rand(BEES_X_DIM*BEES_Y_DIM),[BEES_X_DIM,BEES_Y_DIM])
                HIVE_STATE_TEMP=np.heaviside(HIVE_STATE_TEMP,0)

            HIVE_STATE_TEMP_SALT=np.real(np.fft.ifft2(np.fft.fft2(HIVE_STATE[t-1])*np.fft.fft2(S)))
            HIVE_STATE_TEMP_SALT=np.heaviside(HIVE_STATE_TEMP_SALT-0.5,1)
            HIVE_STATE_TEMP_SALT=CHANCE_OF_SALTATORY_PROP*HIVE_STATE_TEMP_SALT\
                -np.resize(np.random.rand(BEES_X_DIM*BEES_Y_DIM),[BEES_X_DIM,BEES_Y_DIM])
            HIVE_STATE_TEMP_SALT=np.heaviside(HIVE_STATE_TEMP_SALT,0)

            HIVE_STATE_TEMP=np.heaviside(HIVE_STATE_TEMP+HIVE_STATE_TEMP_SALT,0)


            for col_ind in range(len(Hive)):
                for row_ind in range(len(Hive[col_ind])):
                    if HIVE_STATE_TEMP[col_ind,row_ind]==1:
                        Hive[col_ind][row_ind].update_pulse(True)
                    else:
                        Hive[col_ind][row_ind].update_pulse()

            HIVE_STATE[t]= Helper.bit_map_in_int(Hive)

        # This simply updates the display window.
        if DISPLAY:
            Helper.print_hive(Hive, surf, ((int)(BEES_X_SIZE), (int)(BEES_Y_SIZE)))  # runs the display

    if TIME and not ret:
        print("--- %s seconds ---\n" % (time.time() - start_time))

    # This actually takes a comparably insignificant amount of time wrt the rest of the code
    NUMBER_PARTICIPANTS = np.sum(np.sum(HIVE_STATE,1),1)
    WAVE_TIME=np.int_(np.sum(np.heaviside(NUMBER_PARTICIPANTS,0)))

    SPEEDS=np.zeros([WAVE_TIME,BEES_X_DIM,BEES_Y_DIM])
    NEW_BEES=np.heaviside(HIVE_STATE[1:]-HIVE_STATE[:TOTAL_TIME-1],0)

    for t in range(1,WAVE_TIME):
        SPEEDS[t]=NEW_BEES[t-1]*Dist_matrix/(20*t)
    if plots:
        plt.figure()
        plt.plot(NUMBER_PARTICIPANTS),plt.ylabel('Number Shimmering Bees'),plt.xlabel('time (20 ms)')
        plt.figure()
        plt.plot((np.sum(np.sum(SPEEDS,1),1)/NUMBER_PARTICIPANTS[:WAVE_TIME])[1:]),plt.ylabel('Wave speed (mm/ms)'),plt.xlabel('time (20 ms)')
        print("Wave lasted %s seconds" % (0.02*WAVE_TIME))
    if ret:
        #Need to calculate average wavespeed and max number of participants
        #placeholders below
        return(["average wavespeed", 0.02*WAVE_TIME, "max number of participants"])