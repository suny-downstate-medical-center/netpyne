# Example of saving and output data formats

This example generates a simple network with 3 populations and 3 connectivity rules. It then simulates the network, plots some figures, and saves the different model components to JSON.

## List of files

- **init.py**: python script to create network, run simulation, generate output figs, and save network components to different json files.

- **cfg.py**: contains SimConfig object with the simulation configuration options (e.g. duration, traces to record, etc)

- **netParams.py**: script with network parameters (high-level abstract specifications), including populations, cell properties, connectivity rules, etc

- **out_netParams.json**: JSON with network parameters (high-level abstract specifications), including populations, cell properties, connectivity rules, etc

- **out_netInstance.json**: JSON with network instance, including all cell-to-cell connections. Note: connections are included within each postsynaptic cell.

- **out_netInstanceCompact.json**: JSON with network instance using compact format: each conn is stored as a list instead of a dict. Note: connections are included within each postsynaptic cell.

- **out_netParams_netInstance.json**: JSON with both network params and network instance

- **out_simConfig.json**: JSON with simulation configuration options.

- **out_simData.json**: JSON with simulation output data, including spike times and voltage traces.

- **out_raster.png**: Raster plot.

- **out_V_cell0.png**: Voltage trace recodrding of cell 0.

- **out_net2D.png**: 2D representation of network cells and connections.

## Data structure

- **netParams** and **simConfig**: See metadata description here https://github.com/Neurosim-lab/netpyne/blob/development/netpyne/metadata/metadata.py

- **net**: See http://neurosimlab.com/netpyne/reference.html#netpyne-data-model-structure-of-instantiated-network-and-output-data
