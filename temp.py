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
