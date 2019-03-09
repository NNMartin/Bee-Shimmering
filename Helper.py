

def print_hive(hive, TITLE):
    """
    :param hive: [][] Bees
    :return:
    """
    print(TITLE)
    printer = [""]*len(hive)
    for x in hive:
        for y in range(len(x)):
            if x[y].is_it_active():
                printer[y] += "1"
            else:
                printer[y] += "0"
    for line in printer:
        print(line)
    print()
