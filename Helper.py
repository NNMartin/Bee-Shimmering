import pygame


def print_hive(hive, surf):
    """
    :param hive: [][] Bees
    :param surf: pygame.Surface
    :return:
    """
    h_map = bit_map(hive)
    for x in range(len(h_map)):
        for y in range(len(h_map[x])):
            if h_map[x][y] == "1":
                pygame.draw.line(surf, (255, 255, 255), (x, y), (x, y), 1)
            else:
                pygame.draw.line(surf, (0, 0, 0), (x, y), (x, y), 1)
    pygame.display.update()


def bit_map(hive):
    """
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
