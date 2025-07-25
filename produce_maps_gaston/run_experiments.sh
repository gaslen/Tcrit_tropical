#!/bin/bash

# Run Batch 1 in parallel
echo "Start produce_Tcrit_map.py, produce_data_all_species.py, produce_species_presence_map.py"
python produce_Tcrit_map.py &
python produce_data_all_species.py &
python produce_species_presence_map.py &
wait  # Wait for all processes in Batch 1 to finish

echo "Completed. Starting get_TSM_per_year_future.py, biome_continent_mean_per_year.py "

# Run Batch 2 in parallel
python get_TSM_per_year_future.py &
python biome_continent_mean_per_year.py &
wait  # Wait for all processes in Batch 2 to finish

echo "Batch 2 completed. Starting slope.py, skewness_map.py"

# Run Batch 3 sequentially
python slope.py && python skewness_map.py
wait 
echo "Batch 3 completed. Starting slope_tairmax.py"
python slope_tairmax.py
wait 
echo "All experiments completed."