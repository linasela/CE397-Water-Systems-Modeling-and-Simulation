# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 12:54:21 2025

@author: ps28866
"""

#import packages
import wntr
import matplotlib.pyplot as plt
import magnets as mg

plt.close('all') # close all open figures

units = 15850.3 # cms to gpm

inp = 'networks/Net1.inp'

#----------------------------------------------------------------
# reduce model

keep_nodes = ['11','12','13','21','22','23','31'] # nodes to keep

#call model reduction
wnR = mg.reduction.reduce_model(inp_file = inp, nodes_to_keep = keep_nodes, save_filename = 'networks/Net1_R1')  # wnR is a wntr network model

# create original wn model
wn = wntr.network.WaterNetworkModel(inp)

fig, ax = plt.subplots(1,2,figsize=(10,4))
wntr.graphics.plot_network(wn, ax = ax[0])
wntr.graphics.plot_network(wnR, ax = ax[1])


# compare pump flow and tank head
#-------------------------------------------------------------------------------------------
# simulate original model
sim = wntr.sim.EpanetSimulator(wn)
results = sim.run_sim()
results_tank = results.node['pressure']['2']
results_pump = results.link['flowrate']['9']*units

# simulate reduce model model
simR = wntr.sim.EpanetSimulator(wnR)
resultsR = simR.run_sim()
results_tankR = resultsR.node['pressure']['2']
results_pumpR = resultsR.link['flowrate']['9']*units 

time_hours = results_tank.index / 3600  # Convert seconds to hours


# make plots
#-------------------------------------------------------------------------------------------
fig, ax = plt.subplots(1,2,figsize=(10,4))
# tank
ax[0].plot(time_hours, results_tank, color='blue', linewidth=2, alpha=0.5)
ax[0].plot(time_hours, results_tankR, color='red', linestyle = '--', linewidth=2, alpha=0.5)
ax[0].set_title('Tank')
ax[0].set_xlabel('Time [hr]')
ax[0].set_ylabel('Tank water level [m]')
# pumps
ax[1].plot(time_hours, results_pump, color='blue', linewidth=2, alpha=0.5)
ax[1].plot(time_hours, results_pumpR, color='red', linestyle = '--', linewidth=2, alpha=0.5)
ax[1].set_title('Pump')
ax[1].set_xlabel('Time [hr]')
ax[1].set_ylabel('Pump flow [gpm]')

ax[1].legend(['Original model', 'Reduced model'])

plt.show()
