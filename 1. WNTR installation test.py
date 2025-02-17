# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 20:35:29 2025

@author: ps28866
"""
import wntr
import matplotlib.pyplot as plt # Visualization

plt.close('all') # close all open figures

# Create a WaterNetworkModel from an EPANET INP file
wn = wntr.network.WaterNetworkModel('networks/Net3.inp')

# Plot a basic network graphic
ax = wntr.graphics.plot_network(wn)

# Simulate hydraulics using EPANET
sim = wntr.sim.EpanetSimulator(wn)
results_EPANET = sim.run_sim()


# View EpanetSimulator pressure results
results_EPANET.node['pressure'].head()

# Plot timeseries of a given node
plt.figure() 
node_pressure = results_EPANET.node['pressure'].loc[:,'10']
ax = node_pressure.plot(title='Node pressure')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Pressure (m)')

# Plot timeseries of tank levels
tank_levels = results_EPANET.node['pressure'].loc[:,wn.tank_name_list]
ax = tank_levels.plot(title='Tank level')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Tank Level (m)')

# Plot timeseries of pump flowrates
pump_flowrates = results_EPANET.link['flowrate'].loc[:,wn.pump_name_list]
ax = pump_flowrates.plot(title='Pump flowrate')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Pump flowrate (m$^3$/s)')

# Plot pressure at hour 5 on the network
pressure_at_5hr = results_EPANET.node['pressure'].loc[5*3600, :]
ax = wntr.graphics.plot_network(wn, node_attribute=pressure_at_5hr, node_size=30, title='Pressure at 5 hours')