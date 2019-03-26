import pygame
import numpy as np

def print_hive(hive, surf, sizes):  # This is the main  hive reprinting function
    """
    :param hive: [][] Bees
    :param surf: pygame.Surface
    :param sizes: (int, int)
    :return:
    """
    # This basically just uses a helper function to create a more easily reader version of the hive to print from;
    # While technically it is not at all necessary; but I didn't want to rewrite to much of my early work; it doesn't
    # decrease the speed of the code too, too much.
    h_map = bit_map_in_int(hive)
    # updates each bee on the screen
    for x in range(len(h_map)):
        for y in range(len(h_map[0])):
            if h_map[x][y] == 1:
                pygame.draw.rect(surf, (255, 255, 255), (x*sizes[0], y*sizes[1], sizes[0], sizes[1]))
            else:
                pygame.draw.rect(surf, (0, 0, 0), (x * sizes[0], y * sizes[1], sizes[0], sizes[1]))
    pygame.display.update()  # This refreshes the screen


def bit_map(hive):
    """Converts a hive into a set strings; which represent the activation states of the hive.
    :param hive:
    :return: [str]
    """
    printer = [""]*len(hive)
    for x in hive:
        for y in range(len(x)):
            if x[y].is_it_active():
                printer[y] += "1"
            else:
                printer[y] += "0"
    return printer

def bit_map_in_int(hive):
    """Converts a hive into a set strings; which represent the activation states of the hive.
    :param hive:
    :return: [str]
    """
    printer = np.empty([len(hive),len(hive[0])])
    for x in range(len(hive)):
        for y in range(len(hive[0])):
            if hive[x][y].is_it_active():
                printer[x,y] = 1
            else:
                printer[x,y] = 0
    return printer

def dist(x1, y1, x2, y2, mods):
    """ Returns euclidean distance
    :param int x1:
    :param int y1:
    :param int x2:
    :param int y2:
    :param (int, int) mods:
    :return: float
    """
    return ((abs(x1-x2) % mods[0])**2 + (abs(y1-y2) % mods[1])**2)**(1/2)
