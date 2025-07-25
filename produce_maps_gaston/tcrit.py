import rasterio as rio
import numpy as np
import sys

sys.path.append("..")
ssp = "1981_2010" 
from utils import version, DATA_PATH
from glob import glob


TCRIT = "mean"

if TCRIT == "min":
    Tcrit_map = rio.open(
        DATA_PATH + f"/outputs/Tcrit_map_min_{ssp}{version}.tif", "r"
    ).read(1)
    Tcrit_map[Tcrit_map == 1000] = np.nan
    Tcrit_map[Tcrit_map == 0] = np.nan
elif TCRIT == "mean":
    Tcrit_map = rio.open(
        DATA_PATH + f"/outputs/Tcrit_map_mean_{ssp}{version}.tif", "r"
    ).read(1)
    Tcrit_map[Tcrit_map == 0] = np.nan
elif TCRIT == "max":
    Tcrit_map = rio.open(
        DATA_PATH + f"/outputs/Tcrit_map_max_{ssp}{version}.tif", "r"
    ).read(1)
    Tcrit_map[Tcrit_map == 0] = np.nan

data_both_biomes = np.zeros(Tcrit_map.shape, dtype=bool)

biomes = [
    "Tropical & Subtropical Moist Broadleaf Forests",
    "Tropical & Subtropical Dry Broadleaf Forests",
]
biome_files = [i for i in glob(DATA_PATH + "/Ecoregions2017/*.tif") if "N_A" not in i]
biome_files = [i for b in biomes for i in biome_files if b in i]
for biome_file in biome_files:
    data_biome = rio.open(biome_file, "r").read(1).squeeze()
    data_biome = data_biome.astype(bool)
    data_both_biomes += data_biome
