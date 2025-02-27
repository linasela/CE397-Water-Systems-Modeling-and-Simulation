# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:11:12 2025

@author: ps28866
"""

import wntr
import matplotlib.pyplot as plt
plt.close('all') # close all open figures

# Load the Net3 model
inp_file = 'networks/Net3.inp'
wn = wntr.network.WaterNetworkModel(inp_file)
# set water age simulation
wn.options.quality.parameter = 'AGE'

# get tank name (get tank 1)
tank = wn.get_node('1')

# define mixing model
mixing_models = 'MIXED'

# set tank mixing model
tank.mixing_model = mixing_models

# run simulation
sim = wntr.sim.EpanetSimulator(wn)
results_mixed = sim.run_sim()

# get tank water age
tank_mixed = results_mixed.node['quality'].loc[:,'1']/3600
time_hours = tank_mixed.index / 3600  # Convert seconds to hours

# define mixing model
mixing_models = 'FIFO'

# set tank mixing model
tank.mixing_model = mixing_models

# run simulation
sim = wntr.sim.EpanetSimulator(wn)
results_fifo = sim.run_sim()

# get tank water age
tank_fifo = results_fifo.node['quality'].loc[:,'1']/3600

# define mixing model
mixing_models = 'LIFO'

# set tank mixing model
tank.mixing_model = mixing_models

# run simulation
sim = wntr.sim.EpanetSimulator(wn)
results_lifo = sim.run_sim()

# get tank water age
tank_lifo = results_lifo.node['quality'].loc[:,'1']/3600


# Plot timeseries
plt.figure() 
plt.plot(time_hours, tank_mixed)
plt.plot(time_hours, tank_fifo)
plt.plot(time_hours, tank_lifo)
# Formatting the plot
plt.xlabel('Time (hours)')
plt.ylabel('Water age (hours)')
plt.title('Water age Time Series at Tank 1')
plt.legend(['mixed','fifo','lifo'])
plt.grid(True)
plt.show()








# # more efficient 
# # Define mixing models to compare
# mixing_models = ['MIXED', 'FIFO', 'LIFO']
# results = {}

# # Run simulation for each mixing model
# for model in mixing_models:
#     # Set the tank mixing model
#     wn.get_node(tank.name).mixing_model = model
    
#     # Run water quality simulation (water age analysis)
#     sim = wntr.sim.EpanetSimulator(wn)
#     results[model] = sim.run_sim()

# # Select a node to compare results (change as needed)
# compare_node = '1'  # Replace with a valid junction from Net3

# # Plot results
# plt.figure(figsize=(10, 6))

# for model in mixing_models:
#     age = results[model].node['quality'][compare_node] / 3600  # Convert seconds to hours
#     plt.plot(age.index/3600, age, label=f'Tank Mixing: {model}')

# plt.xlabel('Time (hours)')
# plt.ylabel('Water Age (hours)')
# plt.title(f'Water Age Comparison at Node {compare_node}')
# plt.legend()
# plt.grid(True)
# plt.show()
