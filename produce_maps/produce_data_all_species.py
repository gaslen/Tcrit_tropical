import rasterio as rio
import numpy as np
from os.path import join
from tqdm import tqdm


import sys

sys.path.append("..")
from utils import (
    ssp,
    scale_img,
    modis_files,
    path_species,
    df,
    list_species,
    version,
    DATA_PATH,
)


if __name__ == "__main__":
    modis_shape = rio.open(modis_files[0], "r").shape
    meta = rio.open(modis_files[0], "r").meta
    meta.update(compress="LZW")
    total_count = np.zeros(modis_shape, dtype=np.uint8)
    for i, sp in enumerate(tqdm(list_species, total=len(list_species))):
        threshold_temp = float(
            min(df[df["Plant species clean"] == sp]["Thermal Tolerance_deg.C"])
        )
        merged_sp = join(path_species, sp)
        sdm_1980 = rio.open(join(merged_sp, f"{sp}_covariates_{ssp}.tif"), "r")
        scaled_sdm_1980, window_sdm_1980 = scale_img(
            join(merged_sp, f"{sp}_covariates_{ssp}.tif"), modis_files[0]
        )
        sp_map = np.zeros(modis_shape, dtype=bool)
        sdm_1980_int_slice = (
            slice(
                round(window_sdm_1980[0].start), round(window_sdm_1980[0].stop), None
            ),
            slice(
                round(window_sdm_1980[1].start), round(window_sdm_1980[1].stop), None
            ),
        )
        sp_map[sdm_1980_int_slice] = scaled_sdm_1980
        total_count += sp_map.astype(bool).astype(np.uint8)
    with rio.open(
        DATA_PATH + f"/outputs/species_above_threshold_{ssp}{version}.tif", "w", **meta
    ) as f:  # _: v11, nothing: v10
        f.write(total_count, indexes=1)
