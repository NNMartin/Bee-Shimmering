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
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc

# setting a seed. We can change this later, but useful when running simulations
# for a single parameter.
np.random.seed(10)

def simulation(REFRACTION=40, ACTIVATION=3, TOTAL_TIME=60,
                CHANCE_TO_BE_ACTIVATABLE=0.58, 
                CHANCE_OF_SALTATORY_PROP=0.001, BEES_SALT_LEN=30.0, 
                STRENGTH=10.0, PATTERN='geometric_scaled',RADIUS=3, EXP=1,
                TIME = False, plots=False, ret=False, DISPLAY = False, 
                MOVIE_SAVE=False,MOVIE_NAME='BEES'):
    """
    :param REFRACTION: how many ticks the bee must rest for between activations
    :param int ACTIVATION: how many ticks the bee will remain active for
    :param int TOTAL_TIME: The number of time steps the simulation will run for
    :param double CHANCE_TO_BE_ACTIVATABLE: The probability that it is even possible to activate the bee
    :param double CHANCE_OF_SALTATORY_PROP: This is the probability that a bee activates in the far neighborhood
    :param double BEES_SALT_LEN: saltatory radius in mm!!!
    
    Let's keep these parameters constant during parameter space searches:
    :param double STRENGTH: sum of all elements of the relation matrix
    :param string PATTERN: pattern of the relation matrix
    :param int RADIUS: relation matrix size
    :param double EXP: exponent to raise the relation matrix to (long vs. short range signalling)
    
    :param bool TIME: Whether to time the length of code running
    :param bool plots: Whether to show the plots or not
    :param bool ret: whether or not to return simulation quantities
    :param bool DISPLAY: Whether to show display or not
    :param bool MOVIE_SAVE: Whether to save a movie with name:
    :param string MOVIE_NAME

    :return list: Returns a list of quantities

    Time step is assumed to be 20ms. If <ret> is True, returns a list containing:
    wavespeed,
    """

    if TIME:
        start_time = time.time()
    else:
        start_time = 0

    TIME_STEP = 0.02 #20 ms
    BEES_X_WIDTH = 6.0 #6 mm
    BEES_Y_WIDTH = 3*BEES_X_WIDTH #Let's keep this constant
    ACTIVATION_MODE = 1 #1 = choose to activate on a per signal, 0 = choose to ignore all
    BEES_X_DIM = 100  # This is the size of the hive in the X direction, in number of bees
    BEES_Y_DIM = 100  # This is the size of the hive in the Y direction, in number of bees
    Threshold = 0.5
    #a matrix of distances to (0,0) in units mm
    DIST_MATRIX = Helper.geo_dist_matrix(BEES_X_WIDTH,BEES_Y_WIDTH,BEES_X_DIM,BEES_Y_DIM) 
    BEES_X_SIZE = 1  # The size of the Bee in the X direction in pixels
    BEES_Y_SIZE = 3*BEES_X_SIZE  # The size of the Bee in the Y direction

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
    HEX_GRID=False
    if HEX_GRID:
        for x in range(BEES_X_DIM):
            Bee_col = []
            for y in range(BEES_Y_DIM):
                Bee_col.append(Bee_Files.Bee(REFRACTION, ACTIVATION, np.mod(x+y,2)==1))
                Hive.append(Bee_col)
    else: #Square grid
        for x in range(BEES_X_DIM):
            Bee_col = []
            for y in range(BEES_Y_DIM):
                Bee_col.append(Bee_Files.Bee(REFRACTION, ACTIVATION, (1-ACTIVATION_MODE)*random() <= CHANCE_TO_BE_ACTIVATABLE))
                Hive.append(Bee_col)                


    # This creates the generator bee; to be frank this could also have been done with a bit more elegance, but it was
    # creating a few to many bugs in the first version of the code; so I made it manual, it's a quick fix to make this work
    # for multiple generator bees; if you can't do it just let me know and I'll write a patch
    generator_location = (0, 0)
    Hive[generator_location[0]][generator_location[1]] = Bee_Files.GeneratorBee(REFRACTION, ACTIVATION, True)

    #R is the relation matrix. It calls a pattern from the helper file. Let's stick with geometric_scaled for simulations
    R = Helper.relation_matrix(PATTERN,BEES_X_WIDTH,BEES_Y_WIDTH,BEES_X_DIM,BEES_Y_DIM,STRENGTH,RADIUS)**EXP
    #S is the saltatoric matrix. Here I'vewritten it so it's the units that are less than or equal to
    #BEES_SALT_DIM (in units of mm!) away from (0,0).
    S=np.heaviside(BEES_SALT_LEN-DIST_MATRIX,1)

    #This is a matrix that will be 1 at (t,x,y) if the bee at (t,x,y) is activated and 0 otherwise;
    #updated at the end of each loop.
    ACTIVE_BEES=np.zeros([TOTAL_TIME,BEES_X_DIM,BEES_Y_DIM])
    
    
    # actual simulation; this is just a loop that runs for a certain number of iterations
    for t in range(TOTAL_TIME):
        if t == 0:  # This basically just makes sure that the generator bee activates
            Hive[generator_location[0]][generator_location[1]].activate()
            ACTIVE_BEES[0,generator_location[0],generator_location[1]]=1

        else:  # This is what the the actual iteration does
            #Take a copy of the previously activated bees:
            PREV_ACT_BEES=np.copy(ACTIVE_BEES[t-1])
            #This convolutes R with PREV_ACT_BEES to get a matrix of how much act. signal eahc bee is receiving
            ACT_SIGNAL=np.real(np.fft.ifft2(np.fft.fft2(PREV_ACT_BEES)*np.fft.fft2(R)))
            #This makes a matrix only with bees above the threshold (I have to use 0.99.. because the 
            #fft has a very small error on the order of e-17 and might otherwise clip signals at 1 if I don't do this)
            ACT_SIGNAL=np.heaviside(ACT_SIGNAL/Threshold-0.9999999,1)
            #This randomly drops signals with a chance of 1-CHANCE_TO_BE_ACTIVATABLE
            if ACTIVATION_MODE==1:
                ACT_SIGNAL=CHANCE_TO_BE_ACTIVATABLE*ACT_SIGNAL\
                -np.resize(np.random.rand(BEES_X_DIM*BEES_Y_DIM),[BEES_X_DIM,BEES_Y_DIM])
                ACT_SIGNAL=np.heaviside(ACT_SIGNAL,0)
            
            #Makes a matrix of bees that could salt. activate
            SALT_ACT_SIGNAL=np.real(np.fft.ifft2(np.fft.fft2(PREV_ACT_BEES)*np.fft.fft2(S)))
            SALT_ACT_SIGNAL=np.heaviside(SALT_ACT_SIGNAL-0.001,1)
            #Drops signals with a 1-CHANCE_OF_SALTATORY_PROP chance
            SALT_ACT_SIGNAL=CHANCE_OF_SALTATORY_PROP*SALT_ACT_SIGNAL\
                -np.resize(np.random.rand(BEES_X_DIM*BEES_Y_DIM),[BEES_X_DIM,BEES_Y_DIM])
            SALT_ACT_SIGNAL=np.heaviside(SALT_ACT_SIGNAL,0)

            #GETS the total activation signal with salt.
            ACT_SIGNAL=np.heaviside(ACT_SIGNAL+SALT_ACT_SIGNAL,0)

            #Updates the hive
            for col_ind in range(len(Hive)):
                for row_ind in range(len(Hive[col_ind])):
                    if ACT_SIGNAL[col_ind,row_ind]==1:
                        Hive[col_ind][row_ind].update_pulse(True)
                    else:
                        Hive[col_ind][row_ind].update_pulse()
            
            #Updates ACTIVE_BEES
            ACTIVE_BEES[t]= Helper.bit_map_in_int(Hive)

        # This simply updates the display window.
        if DISPLAY:
            Helper.print_hive(Hive, surf, ((int)(BEES_X_SIZE), (int)(BEES_Y_SIZE)))  # runs the display

    if TIME and not ret:
        print("--- %s seconds ---\n" % (time.time() - start_time))

    # This actually takes a comparably insignificant amount of time wrt the rest of the code
    #Takes a sum of the number of active bees in each frame
    NUMBER_PARTICIPANTS = np.sum(np.sum(ACTIVE_BEES,1),1)
    #Calculates the nu ber of timesteps there was an active bee
    WAVE_TIME=np.int_(np.sum(np.heaviside(NUMBER_PARTICIPANTS,0)))

    #Will be a matrix with the value of the bee at (t,x,y) at the wavespeed (dist to (0,0)/timestep 
    #of the bee if it activated then and 0 otherwise.
    SPEEDS_MATRIX=np.zeros([WAVE_TIME,BEES_X_DIM,BEES_Y_DIM])
    #This will have the average speed per time step
    SPEEDS=np.zeros(TOTAL_TIME)
    #Takes the difference between subsequent frames to see which new bees activated
    NEW_BEES=np.heaviside(ACTIVE_BEES[1:]-ACTIVE_BEES[:TOTAL_TIME-1],0)
    #I know, if loop, bad form, but doing it without would involve np.tile() and I don't want to think that hard
    for t in range(1,WAVE_TIME):
        #Updates speeds in m/s=mm/ms (1000* because TIME_STEP is in s)
        SPEEDS_MATRIX[t]=NEW_BEES[t-1]*DIST_MATRIX/(1000*TIME_STEP*t)
    
    SPEEDS[:WAVE_TIME]=np.sum(np.sum(SPEEDS_MATRIX,1),1)/NUMBER_PARTICIPANTS[:WAVE_TIME]
    
    if plots:
        plt.figure()
        plt.plot(20*np.arange(TOTAL_TIME),NUMBER_PARTICIPANTS),plt.ylabel('Number Shimmering Bees'),plt.xlabel('time (ms)')
        plt.figure()
        plt.plot(20*np.arange(TOTAL_TIME),SPEEDS),plt.ylabel('Wave speed (m/s)'),plt.xlabel('time (ms)')
        print("Wave lasted %s seconds" % (TIME_STEP*WAVE_TIME))
    if ret:
        #Need to calculate average wavespeed and max number of participants
        #placeholders below
        return(["average wavespeed", TIME_STEP*WAVE_TIME, "max number of participants"])
    
    if MOVIE_SAVE:
        FPS=20
        fourcc = VideoWriter_fourcc(*'XVID')
        video = VideoWriter(MOVIE_NAME+'.avi', fourcc, float(FPS), (BEES_X_DIM*BEES_X_SIZE, BEES_Y_DIM*BEES_Y_SIZE))
        T_ACT_BEES=np.empty([TOTAL_TIME,BEES_Y_DIM, BEES_X_DIM,3])
        T_ACT_BEES[:,:,:,0]=255*np.transpose(ACTIVE_BEES,axes=(0,2,1))
        T_ACT_BEES[:,:,:,1]=255*np.transpose(ACTIVE_BEES,axes=(0,2,1))
        T_ACT_BEES[:,:,:,2]=255*np.transpose(ACTIVE_BEES,axes=(0,2,1))
        T_ACT_BEES=np.repeat(T_ACT_BEES,BEES_Y_SIZE,axis=1)
        T_ACT_BEES=np.repeat(T_ACT_BEES,BEES_X_SIZE,axis=2)
        
        for t in range(TOTAL_TIME):
           frame=(T_ACT_BEES[t]).astype(np.uint8)
           video.write(frame)
            
        video.release()
            
            