import setup


# Create new Figure and an Axes which fills it.
fig = plt.figure(figsize=(7, 7))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, 1), ax.set_xticks([])
ax.set_ylim(0, 1), ax.set_yticks([])

# Construct the scatter which we will update during animation
scat = ax.scatter(PlotHive['position'][:, 0], PlotHive['position'][:, 1],
                  lw=0.5, edgecolors=PlotHive['colour'], facecolors='none')



# at the moment these numbers are just place holders for a PoC; must be odd by odd, though not necessarily rectangular.
relation_matrix = [[1/(68**(1/2)), 1/(29**(1/2)), 1/2, 1/(29**(1/2)), 1/(68**(1/2))],
                   [1/(26**(1/2)), 1, 1, 1, 1/(26**(1/2))], [1/5, 1, 0, 1, 1/5],
                   [1/(26**(1/2)), 1, 1, 1, 1/(26**(1/2))],
                   [1/(68**(1/2)), 1/(29**(1/2)), 1/2, 1/(29**(1/2)), 1/(68**(1/2))]]

# This is the threshold to which the bee needs to receive input before becoming active, Honestly probably should be
# replaced with something more complicated in the Bees at a later date
Threshold = 0.5

act_bees = [[generator_location[0], generator_location[1]]]

def update(frame_number):

    global act_bees
    temp = []
    if frame_number == 0:  # This basically just makes sure that the generator bee activates
        Hive[generator_location[0]][generator_location[1]].activate()
    Last_Hive_State = deepcopy(Hive)  # To avoid object pointer issues we need to create a deep copy
    affected_bees = {}
    for bee in act_bees:
        for mod_x_ind in range(len(relation_matrix)):
            x_modifier = mod_x_ind - ((len(relation_matrix)-1)//2)
            for mod_y_ind in range(len(relation_matrix[mod_x_ind])):
                y_modifier = mod_y_ind - ((len(relation_matrix[mod_x_ind]) - 1) // 2)
                pos = ((bee[0]+x_modifier) % (BEES_X_DIM-1),(bee[1]+y_modifier) % (BEES_Y_DIM-1))
                if pos in affected_bees:
                    affected_bees[pos] += relation_matrix[mod_x_ind][mod_y_ind]
                else:
                    affected_bees[pos] = relation_matrix[mod_x_ind][mod_y_ind]
    # If the bee receives enough of a signal it will be told to activate, else it will not be.
    for bee in affected_bees:
        if affected_bees[bee] >= Threshold:
            Hive[bee[0]][bee[1]].update_pulse(True)
        else:
            Hive[bee[0]][bee[1]].update_pulse()
        if Hive[bee[0]][bee[1]].is_active:
            a = blk
            temp.append(bee)
        else:
            a = wht
        index = HiveToHiveMap[bee]
        PlotHive[index][1] = a

    act_bees = temp

    # Update the scatter collection with the new colors.
    scat.set_edgecolors(PlotHive['colour'])





# Construct the animation, using the update function as the animation director.
animation = FuncAnimation(fig, update, interval=400)
plt.show()
