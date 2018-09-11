# Example of saving and output data formats

This example generates a simple network with 3 populations and 3 connectivity rules. It then simulates the networ, plots some figures, and saves teh differnet model components to JSON.

## List of files

- **init.py**: python script to create network, run simulation, generate output figs, and save network components to different json files.

- **cfg.py**: contains SimConfig object with the simulation configuration options (e.g. duration, traces to record, etc)

- **netParams.py**: script with network parameters (high-level abstract specifications), including populations, cell properties, connectivity rules, etc

- **out_netParams.json**: JSON with network parameters (high-level abstract specifications), including populations, cell properties, connectivity rules, etc

- **out_netInstance.json**: JSON with network instance, including all cell-to-cell connections. Note: connections are included within each postsynaptic cell.

- **out_netInstanceCompact.json**: JSON with network instance using compact format: each conn is stored as a list instead of a dict. Note: connections are included within each postsynaptic cell.

- **out_netParams_netInstance.json**: JSON with both network params and network instance

- **out_simConfig.json**: JSON with simulation configuration options.

- **out_simData.json**: JSON with simulation ouput data, including spike times and voltage traces.

- **out_raster.png**: Raster plot.

- **out_V_cell0.png**: Voltage trace recodrding of cell 0.

- **out_net2D.png**: 2D representation of network cells and connections.
