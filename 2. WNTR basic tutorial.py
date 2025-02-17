# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 13:07:30 2025

@author: ps28866
"""

# This is a shorter version of the JN file with only a subset of commands

import numpy as np
import wntr
import matplotlib.pyplot as plt # Visualization

plt.close('all') # close all open figures

# Create a WaterNetworkModel from an EPANET INP file
wn = wntr.network.WaterNetworkModel('networks/Net3.inp')

# Plot a basic network graphic
ax = wntr.graphics.plot_network(wn)


# %% This creates a new section

all_pipe_diameters = wn.query_link_attribute('diameter')
all_pipe_diameters.head()

large_pipe_diameters = wn.query_link_attribute('diameter', np.greater, 12*0.0254)
print("Number of pipes:", len(all_pipe_diameters))
print("Number of pipes > 12 inches:", len(large_pipe_diameters))

ax = wntr.graphics.plot_network(wn, link_attribute=large_pipe_diameters, node_size=0, link_width=2, title="Pipes with diameter > 12 inches")