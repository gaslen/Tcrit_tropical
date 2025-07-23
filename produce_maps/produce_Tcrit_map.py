"""
Compute Tcrit maps
"""

import rasterio as rio
import numpy as np
from os.path import join, expanduser
from tqdm import tqdm

import sys

sys.path.append("..")
from utils import (
    scale_img,
    path_species,
    df,
    list_species,
    meta_full_map,
    shape_full_map,
    version,
    DATA_PATH,
)


if __name__ == "__main__":
    meta = meta_full_map
    meta.update(compress="LZW")
    for ssp in ["1981_2010", "2071_2100_ssp370", "2041_2070_ssp370"]:
        output_max = np.zeros(shape_full_map)
        total_count = np.zeros(shape_full_map)
        temp_count = np.zeros(shape_full_map)
        output_min = np.full(shape_full_map, 1000.0)
        for sp in tqdm(list_species, total=len(list_species)):
            threshold_temp = float(
                np.mean(df[df["Plant species clean"] == sp]["Thermal Tolerance_deg.C"])
            )
            merged_sp = join(path_species, sp)
            scaled_sdm_1980, window_sdm_1980 = scale_img(
                join(merged_sp, f"{sp}_covariates_{ssp}.tif"),
                DATA_PATH + "/dense_vegetation/plant_fraction_LST_Day.tif",
            )
            # fit sdm data into a worldwide map
            sp_map = np.zeros(shape_full_map, dtype=bool)
            sdm_1980_int_slice = (
                slice(
                    round(window_sdm_1980[0].start),
                    round(window_sdm_1980[0].stop),
                    None,
                ),
                slice(
                    round(window_sdm_1980[1].start),
                    round(window_sdm_1980[1].stop),
                    None,
                ),
            )
            sp_map[sdm_1980_int_slice] = scaled_sdm_1980
            threshold_map = threshold_temp * sp_map
            output_max = np.maximum(threshold_map, output_max)
            temp_count += threshold_map
            total_count += threshold_map.astype(bool)
            threshold_map[threshold_map == 0] = np.nan
            output_min[~np.isnan(threshold_map)] = np.minimum(
                output_min, threshold_map
            )[~np.isnan(threshold_map)]
        meta["dtype"] = "float64"
        meta["compress"] = "LZW"
        with rio.open(
            expanduser(DATA_PATH + f"/outputs/Tcrit_map_max_{ssp}{version}.tif"),
            "w",
            **meta,
        ) as f:  # _: v11, nothing: v10
            f.write(output_max, indexes=1)
        with rio.open(
            expanduser(DATA_PATH + f"/outputs/Tcrit_map_min_{ssp}{version}.tif"),
            "w",
            **meta,
        ) as f:
            f.write(output_min, indexes=1)
        with rio.open(
            expanduser(DATA_PATH + f"/outputs/Tcrit_map_mean_{ssp}{version}.tif"),
            "w",
            **meta,
        ) as f:
            f.write(temp_count / total_count, indexes=1)
        with rio.open(
            expanduser(DATA_PATH + f"/outputs/species_count_map_{ssp}{version}.tif"),
            "w",
            **meta,
        ) as f:
            f.write(total_count, indexes=1)
