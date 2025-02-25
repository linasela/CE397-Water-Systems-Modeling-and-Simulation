# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 10:08:52 2025

@author: ps28866
"""

import geopandas as gpd
from shapely.geometry import box
import matplotlib.pylab as plt
import wntr

plt.close('all') # close all open figures


import os

if not os.path.isdir('geojsons'):
    os.makedirs('geojsons')
    
# The following line defines coordinates used to zoom in on network graphics
zoom_coords = [(5.75e6, 5.79e6), (3.82e6, 3.85e6)] 

# %% Water Network Model

# Create a WaterNetworkModel from an EPANET INP file
inp_file = 'networks/ky10.inp'
wn = wntr.network.WaterNetworkModel(inp_file)

# Compute total pipe length
length = wn.query_link_attribute('length')
total_length = length.sum() # m
print('Total pipe length =', total_length, 'm, =', total_length*3.28084, 'ft')

# Compute average expected demand per day 
average_expected_demand = wntr.metrics.average_expected_demand(wn) # m^3/s
average_volume_per_day = average_expected_demand*(24*3600) # m^3
total_water_use = average_volume_per_day.sum() # m^3
print('Total water use =', total_water_use, 'm^3, =', total_water_use*264.172/1e6, 'million gallons')

# Estimate population using the default average volume of water consumed per capita per day of 200 gallons/day
population = wntr.metrics.population(wn) 
total_population = population.sum()
print('Total population =', total_population)

# Create a basic network graphic, showing junction elevation
# Note, the remaining graphics in this tutorial are created from the geospatial data directly, rather than the `plot_network` function.
# The `plot_network` function currently does not include vertices.
ax = wntr.graphics.plot_network(wn, node_attribute='elevation', node_range=(175, 300), title='ky10 elevation')

# %% GIS

# Convert the WaterNetworkModel to GIS data and set the CRS
wn_gis = wn.to_gis()
wn_gis.junctions.head()
#wn_gis.tanks.head()
#wn_gis.reservoirs.head()
#wn_gis.pipes.head()
#wn_gis.pumps.head()

# Set the CRS to EPSG:3089 (NAD83 / Kentucky Single Zone (ftUS))
crs = 'EPSG:3089'
wn_gis.set_crs(crs)

# Use the GIS data to create a figure of the network
fig, ax = plt.subplots(figsize=(5,5))
ax = wn_gis.pipes.plot(column='diameter', linewidth=1, label='pipes', alpha=0.8, ax=ax, zorder=1)
ax = wn_gis.reservoirs.plot(color='k', marker='s', markersize=60, label='reservoirs', ax=ax)
ax = wn_gis.tanks.plot(color='r', markersize=20, label='tanks', ax=ax)
ax = wn_gis.pumps.centroid.plot(color='b', markersize=20, label='pumps', ax=ax)
ax = wn_gis.valves.centroid.plot(color='c', markersize=20, label='valves', ax=ax)
tmp = ax.axis('off')
# Comment/uncomment the following 2 lines to change the zoom on the network graphic
#tmp = ax.set_xlim(zoom_coords[0])
#tmp = ax.set_ylim(zoom_coords[1])
tmp = plt.legend()

# Store the WaterNetworkModel as a collection of GeoJSON files
wn_gis.write_geojson('geojsons/ky10')

# %% Load landslide and SVI
# Load the landslide data from file and print the CRS to ensure it is in EPSG:3089.  
# The methods `to_crs` and `set_crs` can be used to change coordinate reference systems if needed.
landslide_file = 'data/ky10_landslide_data.geojson'
landslide_data = gpd.read_file(landslide_file).set_index('index') 
print(landslide_data.crs)

landslide_data.head()

# Plot the landslide data along with pipes
ax = landslide_data.plot(color='red', label='Landslide data')
ax = wn_gis.pipes.plot(color='black', linewidth=1, ax=ax)
ax.set_title('Landslide and pipe data')
tmp = ax.axis('off')
# Comment/uncomment the following 2 lines to change the zoom on the network graphic
tmp = ax.set_xlim(zoom_coords[0])
tmp = ax.set_ylim(zoom_coords[1])


# Load the SVI data from file and print the CRS to ensure it is in EPSG:3089.  
# The methods `to_crs` and `set_crs` can be used to change coordinate reference systems if needed.
svi_file = 'data/ky10_svi_data.geojson'
svi_data = gpd.read_file(svi_file).set_index('index') 
print(svi_data.crs)

svi_data.head()

# Plot SVI data and pipes (higher values of SVI are associated with higher vulnerability)
ax = svi_data.plot(column='RPL_THEMES', label='SVI data', cmap='RdYlGn_r', vmin=0, vmax=1, legend=True)
ax = wn_gis.pipes.plot(color='black', linewidth=1, ax=ax)
ax.set_title('SVI and pipe data')
tmp = ax.axis('off')
# Comment/uncomment the following 2 lines to change the zoom on the network graphic
tmp = ax.set_xlim(zoom_coords[0])
tmp = ax.set_ylim(zoom_coords[1])

# %% Buffer
# Create a GeoDataFrame to hold information used in landslide scenarios (initially copied from landslide_data)
# Buffer each landslide polygon by 1000 ft
landslide_scenarios = landslide_data.copy()
landslide_scenarios['geometry'] = landslide_data.buffer(1000)

# Add a prefix to the landslide scenario index to indicate the scenario name
landslide_scenarios.index = 'LS-' + landslide_scenarios.index.astype(str)


# Plot the landslide data, region included in each landslide scenario, and pipes
ax = landslide_scenarios.plot(color='gray', alpha=0.5)
ax = landslide_data.plot(color='red', label='Landslide data', ax=ax)
ax = wn_gis.pipes.plot(color='black', linewidth=1, ax=ax)
ax.set_title('Landslide scenario and pipe data')
tmp = ax.axis('off')
# Comment/uncomment the following 2 lines to change the zoom on the network graphic
tmp = ax.set_xlim(zoom_coords[0])
tmp = ax.set_ylim(zoom_coords[1])

# %% Geo intersections
# Use the intersect function to determine pipes and pipe length that intersects each landslide
A = landslide_scenarios
B = wn_gis.pipes
B_value = 'length'
landslide_intersect = wntr.gis.intersect(A, B, B_value)

# Print results in order of descending total pipe length
landslide_intersect.sort_values('sum', ascending=False).head()

# Add the intersection results to the landslide scenario data
landslide_scenarios[['intersections', 'n', 'total pipe length']] = landslide_intersect[['intersections', 'n', 'sum']]

# Print results in order of descending total pipe length
landslide_scenarios.sort_values('total pipe length', ascending=False).head()

# Plot intersection results
fig, axes = plt.subplots(1,2, figsize=(15,5))

wn_gis.pipes.plot(color='gray', linewidth=1, ax=axes[0])
landslide_scenarios.plot(column='n', vmax=10, legend=True, ax=axes[0])
tmp = axes[0].set_title('Number of pipes that intersect each landslide')
tmp = axes[0].axis('off')
# Comment/uncomment the following 2 lines to change the zoom on the network graphic
tmp = axes[0].set_xlim(zoom_coords[0])
tmp = axes[0].set_ylim(zoom_coords[1])

wn_gis.pipes.plot(color='gray', linewidth=1, ax=axes[1])
landslide_scenarios.plot(column='total pipe length', vmax=10000, legend=True, ax=axes[1])
tmp = axes[1].set_title('Length of pipe that intersect each landslide')
tmp = axes[1].axis('off')
# Comment/uncomment the following 2 lines to change the zoom on the network graphic
tmp = axes[1].set_xlim(zoom_coords[0])
tmp = axes[1].set_ylim(zoom_coords[1])

# %% Assign SVI

# Use the intersect function to determine SVI of each junction.  
A = wn_gis.junctions
B = svi_data
B_value = 'RPL_THEMES'
junction_svi = wntr.gis.intersect(A, B, B_value)

junction_svi.head()

# Add the intersection results (SVI value) to the GIS junction data
wn_gis.junctions['RPL_THEMES'] = junction_svi['mean']

# Plot SVI for each census tract and SVI assigned to each junction
fig, axes = plt.subplots(1,2, figsize=(15,5))

svi_data.plot(column='RPL_THEMES', label='SVI data', vmin=0, vmax=1, legend=True, ax=axes[0])
wn_gis.pipes.plot(color='black', linewidth=1, ax=axes[0])
tmp = axes[0].set_title('Census tract SVI and pipe data')
tmp = axes[0].axis('off')
# Comment/uncomment the following 2 lines to change the zoom on the network graphic
tmp = axes[0].set_xlim(zoom_coords[0])
tmp = axes[0].set_ylim(zoom_coords[1])

wn_gis.pipes.plot(color='gray', linewidth=1, ax=axes[1])
wn_gis.junctions.plot(column='RPL_THEMES', vmin=0, vmax=1, legend=True, ax=axes[1])
tmp = axes[1].set_title('SVI value at each junction')
tmp = axes[1].axis('off')
# Comment/uncomment the following 2 lines to change the zoom on the network graphic
tmp = axes[1].set_xlim(zoom_coords[0])
tmp = axes[1].set_ylim(zoom_coords[1])

# %% Hydraulic simulations
# Create a function to setup the WaterNetworkModel for hydraulic simulations
def model_setup(inp_file):
    wn = wntr.network.WaterNetworkModel(inp_file)
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = 20 # m
    wn.options.hydraulic.minimum_pressure  = 0 # m
    wn.options.time.duration = 48*3600 # s (48 hour simulation)
    return wn


# %% # Run a baseline simulation, with no landslide or damage.  
#------------------------------------------------------------------
wn = model_setup(inp_file)
sim = wntr.sim.EpanetSimulator(wn)
baseline_results = sim.run_sim()

# plot pressure at a given node
node_pressure = baseline_results.node['pressure']['J-417']
time_hours = node_pressure.index / 3600  # Convert seconds to hours
# Plot timeseries of a given node
plt.figure() 
plt.plot(time_hours, node_pressure)
# Formatting the plot
plt.xlabel('Time (hours)')
plt.ylabel('Pressure (m)')
plt.title('Pressure Time Series at Selected Nodes')
plt.legend(['node J-417'])
plt.grid(True)

# plot tank head
tank_pressure = baseline_results.node['pressure']['T-1']
# Plot timeseries of a given node
plt.figure() 
plt.plot(time_hours, tank_pressure)
# Formatting the plot
plt.xlabel('Time (hours)')
plt.ylabel('Water level (m)')
plt.title('Tank water level')
plt.legend(['Tank T-1'])
plt.grid(True)

# %% Landslide simulation
#------------------------------------------------------------------
# choose one scenario
landslide_scenarios_1 = landslide_scenarios.loc[['LS-7003'],:] 

# plot
ax = landslide_scenarios_1.plot(color='blue')
wn_gis.pipes.plot(color='gray', linewidth=1, ax=ax)
tmp = ax.set_title('Landslide scenarios')
tmp = ax.axis('off')

# %% Landslide simulation
# create a new model
wn = model_setup(inp_file)

# close the first pipe
pipe_i = landslide_scenarios_1['intersections'].iloc[0][0]
pipe_object = wn.get_link(pipe_i)
pipe_object.initial_status = 'CLOSED'
#run simulation
sim = wntr.sim.EpanetSimulator(wn)
landslide_results = sim.run_sim()


# plot pressure at a given node for the base and landslide scenarios
node_pressure_1 = landslide_results.node['pressure']['J-417']
time_hours = node_pressure.index / 3600  # Convert seconds to hours
# Plot timeseries of a given node
plt.figure() 
plt.plot(time_hours, node_pressure)
plt.plot(time_hours, node_pressure_1)
# Formatting the plot
plt.xlabel('Time (hours)')
plt.ylabel('Pressure (m)')
plt.title('Pressure Time Series at Selected Nodes')
plt.legend(['baseline','landslide'])
plt.grid(True)

# plot tank head for the base and landslide scenarios
tank_pressure_1 = landslide_results.node['pressure']['T-1']
# Plot timeseries of a given node
plt.figure() 
plt.plot(time_hours, tank_pressure)
plt.plot(time_hours, tank_pressure_1)
# Formatting the plot
plt.xlabel('Time (hours)')
plt.ylabel('Water level (m)')
plt.title('Tank water level')
plt.legend(['baseline','landslide'])
plt.grid(True)


# %% Landslide simulation

# create a new model
wn = model_setup(inp_file)
# close all pipes in that scenario
for pipe_i in landslide_scenarios_1['intersections'].iloc[0]:
    pipe_object = wn.get_link(pipe_i)
    pipe_object.initial_status = 'CLOSED'
    
# run simulation
sim = wntr.sim.EpanetSimulator(wn)
landslide_results = sim.run_sim()


# plot pressure at a given node for the base and landslide scenarios
node_pressure_1 = landslide_results.node['pressure']['J-417']
time_hours = node_pressure.index / 3600  # Convert seconds to hours
# Plot timeseries of a given node
plt.figure() 
plt.plot(time_hours, node_pressure)
plt.plot(time_hours, node_pressure_1)
# Formatting the plot
plt.xlabel('Time (hours)')
plt.ylabel('Pressure (m)')
plt.title('Pressure Time Series at Selected Nodes')
plt.legend(['baseline','landslide'])
plt.grid(True)

# plot tank head for the base and landslide scenarios
tank_pressure_1 = landslide_results.node['pressure']['T-1']
# Plot timeseries of a given node
plt.figure() 
plt.plot(time_hours, tank_pressure)
plt.plot(time_hours, tank_pressure_1)
# Formatting the plot
plt.xlabel('Time (hours)')
plt.ylabel('Water level (m)')
plt.title('Tank water level')
plt.legend(['baseline','landslide'])
plt.grid(True)
