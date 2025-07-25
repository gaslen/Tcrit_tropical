import rasterio as rio
import numpy as np
from tqdm import tqdm
from os.path import join, expanduser

import sys
sys.path.append("..")
from utils import (
    DATA_PATH,
    version,
    list_species, 
    species_df, 
    path_sdms, 
    scale_img,
    meta_full_map,
    shape_full_map
)

meta = meta_full_map
meta.update(compress="LZW")
meta["dtype"] = "float64"
meta["compress"] = "LZW"

for ssp in ["1981_2010", "2071_2100_ssp370", "2041_2070_ssp370"]:
    tcrit_max = np.zeros(shape_full_map)
    tcrit_sum = np.zeros(shape_full_map)
    sps_count = np.zeros(shape_full_map)
    tcrit_min = np.full(shape_full_map, 1000.0)

    for sp in tqdm(list_species, total=len(list_species)):
        sp_tcrit = float(np.mean(species_df[species_df["Plant species clean"] == sp]["Thermal Tolerance_deg.C"]))
        sdm, window_sdm = scale_img(join(path_sdms, sp, f"{sp}_covariates_{ssp}.tif"),
            DATA_PATH + "/dense_vegetation/plant_fraction_LST_Day.tif")
            
        # fit sdm data into a worldwide map
        sp_map = np.zeros(shape_full_map, dtype=bool)
        sdm_1980_int_slice = (slice(round(window_sdm[0].start),round(window_sdm[0].stop),None,),
                              slice(round(window_sdm[1].start),round(window_sdm[1].stop),None,))
        sp_map[sdm_1980_int_slice] = sdm

        sp_tcrit_map = sp_tcrit * sp_map
        tcrit_max = np.maximum(sp_tcrit_map, tcrit_max)
        tcrit_sum += sp_tcrit_map
        sps_count += sp_tcrit_map.astype(bool)
        sp_tcrit_map[sp_tcrit_map == 0] = np.nan
        tcrit_min[~np.isnan(sp_tcrit_map)] = np.minimum(tcrit_min, sp_tcrit_map)[~np.isnan(sp_tcrit_map)]

    with rio.open(expanduser(DATA_PATH + f"/outputs/Tcrit_map_max_{ssp}{version}.tif"), "w", **meta,) as f: 
        f.write(tcrit_max, indexes=1)

    with rio.open(expanduser(DATA_PATH + f"/outputs/Tcrit_map_min_{ssp}{version}.tif"), "w", **meta) as f:
        f.write(tcrit_min, indexes=1)

    with rio.open(expanduser(DATA_PATH + f"/outputs/Tcrit_map_mean_{ssp}{version}.tif"), "w", **meta) as f:
        f.write(tcrit_sum / sps_count, indexes=1)

    with rio.open(expanduser(DATA_PATH + f"/outputs/species_count_map_{ssp}{version}.tif"), "w", **meta) as f:
        f.write(sps_count, indexes=1)
