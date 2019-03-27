import HiveSurface
import pandas as pd
import numpy as np

# parameters to be simulated (more can be added)
t = "Threshold"
act = "Activation Prob"

def run_param_sim(param, start, end, stepsize, csv=False):

    results = pd.DataFrame(columns=[param, "Avg Wave Speed", "Wave Duration",
                            "Max Wave Strength"])
    i = 0
    for p in np.arange(start, end, stepsize):
        if param == t:
            sim = HiveSurface.simulation(Threshold=p, ret=True)
        elif param == act:
            sim = HiveSurface.simulation(HANCE_TO_BE_ACTIVATABLE=p, ret=True)

        results.at[i, param] = p
        results.at[i, "Avg Wave Speed"] = sim[0]
        results.at[i, "Wave Duration"] = sim[1]
        results.at[i, "Max Wave Strength"] = sim[2]
        i += 1
    if csv:
        results.to_csv(param + "_Simulations.csv")
    else:
        return(results)
