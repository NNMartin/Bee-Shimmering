import pygame


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
    h_map = bit_map(hive)
    # updates each bee on the screen
    for x in range(len(h_map)):
        for y in range(len(h_map[x])):
            if h_map[x][y] == "1":
                pygame.draw.line(surf, (255, 255, 255), (x*sizes[0], y*sizes[1]),
                                 ((x+1)*sizes[0]-1, (y+1)*sizes[1]-1), 1)
            else:
                pygame.draw.line(surf, (0, 0, 0), (x*sizes[0], y*sizes[1]),
                                 ((x+1)*sizes[0]-1, (y+1)*sizes[1]-1), 1)
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
