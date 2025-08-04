import rasterio as rio
import numpy as np
from os.path import join, basename, exists

import sys
sys.path.append("..")
from utils import (
    DATA_PATH,
    version,
    geo_slices,
    modis_folder,
    dense_vegetation
)

# mean Tcrit maps with SDMs with climate data from 2041-2070 and 2071-2100 (SSP 3.70)
mean_tcrit_maps = [
    rio.open(DATA_PATH + f"/outputs/Tcrit_map_mean_2041_2070_ssp370{version}.tif", "r").read(1),
    rio.open(DATA_PATH + f"/outputs/Tcrit_map_mean_2071_2100_ssp370{version}.tif", "r").read(1)
]
 
# Binary mask for both considered biomes
data_both_biomes = np.zeros(mean_tcrit_maps[0].shape, dtype=bool)
biomes = [
    "Tropical & Subtropical Moist Broadleaf Forests",
    "Tropical & Subtropical Dry Broadleaf Forests",
]
biome_files = [join(DATA_PATH, f"Ecoregions2017/{b}.tif") for b in biomes]
for biome_file in biome_files:
    data_biome = rio.open(biome_file, "r").read(1).squeeze()
    data_biome = data_biome.astype(bool)
    data_both_biomes += data_biome

# Modis LST data for 2020
with rio.open(join(modis_folder, "2020.tif"), "r") as src:
    lst_2020 = src.read(1)
    lst_2020[dense_vegetation == 0] = np.nan
    lst_2020[~data_both_biomes] = np.nan
    lst_2020[lst_2020 == -1000] = np.nan

# Delta surface temperature maps for 2050 and 2100 with preprocessing function
def process_delta_tsurf(delta_tsurf):
    delta_tsurf[delta_tsurf==-20] = np.nan
    delta_tsurf[dense_vegetation == 0] = np.nan
    delta_tsurf[~data_both_biomes] = np.nan
    return delta_tsurf
delta_tsurf_maps = [
    process_delta_tsurf(rio.open(DATA_PATH + '/2050-2100_temperatures/delta_tsurf_2020_2050.tif', 'r').read(1)),
    process_delta_tsurf(rio.open(DATA_PATH + '/2050-2100_temperatures/delta_tsurf_2020_2100.tif', 'r').read(1))
]

for continent, slice in geo_slices.items():
    for year, tcrit, delta_tsurf in zip(['2050', '2100'], mean_tcrit_maps, delta_tsurf_maps):
        print(continent, year)
        # Compute TSM with future LST (LST+delta Tsurf) 
        outfile = (DATA_PATH + f"/outputs/TSM_{year}_{continent}_{version}.npy")
        tsm = tcrit[slice] - lst_2020[slice] - delta_tsurf[slice]
        np.save(outfile, tsm)

        # Compute TSM with future LST and acclimation 
        outfile_acclim = (DATA_PATH + f"/outputs/TSM_{year}_acclim_{continent}_{version}.npy")
        tsm_acclim = tsm + (delta_tsurf[slice] * 0.38)
        np.save(outfile_acclim, tsm_acclim)