# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 20:35:29 2025

@author: ps28866
"""
import wntr
import matplotlib.pyplot as plt 
import numpy as np

plt.close('all') # close all open figures

# Create a WaterNetworkModel from an EPANET INP file
wn = wntr.network.WaterNetworkModel('networks/Net3.inp')

# set simulation duration to 4 days
wn.options.time.duration = 4*24*3600 # seconds

# Plot a basic network graphic
# ax = wntr.graphics.plot_network(wn)


# %% Hydraulic simulation
#------------------------------------------------------
# Simulate hydraulics using EPANET
sim = wntr.sim.EpanetSimulator(wn)
results = sim.run_sim()

# Get pressure for a given node and adjust time from sec to hours
node_pressure = results.node['pressure'].loc[:,'105']
time_hours = node_pressure.index / 3600  # Convert seconds to hours

# Plot timeseries of a given node
plt.figure() 
plt.plot(time_hours, node_pressure)
# Formatting the plot
plt.xlabel('Time (hours)')
plt.ylabel('Pressure (m)')
plt.title('Pressure Time Series at Selected Nodes')
plt.legend()
plt.grid(True)
plt.show()

# %% Water quality simulation
#------------------------------------------------------
# set water age simulation
wn.options.quality.parameter = 'AGE'

# run new simulation
sim = wntr.sim.EpanetSimulator(wn)
results = sim.run_sim()

# get water age at nodes 183, 105, and 1 (tank); convert to hours
node_water_age = results.node['quality'].loc[:,['105','183','1']]/3600
time_hours = node_water_age.index / 3600  # Convert seconds to hours

# Plot timeseries
plt.figure() 
plt.plot(time_hours, node_water_age)
# Formatting the plot
plt.xlabel('Time (hours)')
plt.ylabel('Water age (hours)')
plt.title('Water age Time Series at Selected Nodes')
plt.legend(['105','183','1'])
plt.grid(True)
plt.show()


#------------------------------------------------------
# plot average water age at 48 hours across the network
age = results.node['quality']
age_48h = age.loc[48*3600]/3600
ax = wntr.graphics.plot_network(wn, node_attribute = age_48h, node_size=50, title = "Water age at 48 (hr)")

#------------------------------------------------------
# plot average water age in the last 48 hours across the network
age = results.node['quality']
age_last_48h = age.loc[age.index[-1]-48*3600:age.index[-1]]
average_age = age_last_48h.mean()/3600 # convert to hours for the plot
ax = wntr.graphics.plot_network(wn, node_attribute = average_age, node_size=50, title = "Average water age the last 48 (hr)")


