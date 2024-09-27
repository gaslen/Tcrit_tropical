import rasterio as rio
import numpy as np
import sys
sys.path.append('..')
from utils import ssp, biome_files


TCRIT = "min" 

if TCRIT == "min":
    Tcrit_map = rio.open(f"/data/gaston/ecostress/ecostress/worldwide/Tcrit_map_min_{ssp}.tif", 'r').read(1)
    Tcrit_map[Tcrit_map==1000] = np.nan
    Tcrit_map[Tcrit_map==0] = np.nan
elif TCRIT == "mean":
    Tcrit_map = rio.open(f"/data/gaston/ecostress/ecostress/worldwide/Tcrit_map_mean_{ssp}.tif", 'r').read(1)
    Tcrit_map[Tcrit_map==0] = np.nan
elif TCRIT == "max":
    Tcrit_map = rio.open(f"/data/gaston/ecostress/ecostress/worldwide/Tcrit_map_max_{ssp}.tif", 'r').read(1)
    Tcrit_map[Tcrit_map==0] = np.nan
    
data_both_biomes = np.zeros(Tcrit_map.shape, dtype=bool)

biomes = ['Tropical & Subtropical Moist Broadleaf Forests', 'Tropical & Subtropical Dry Broadleaf Forests']
biome_files = [i for b in biomes for i in biome_files if b in i]
for biome_file in biome_files:
    data_biome = rio.open(biome_file, 'r').read(1).squeeze()
    data_biome = data_biome.astype(bool)
    data_both_biomes += data_biome