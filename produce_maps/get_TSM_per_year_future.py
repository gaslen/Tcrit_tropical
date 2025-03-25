import numpy as np
import rasterio as rio
import sys

sys.path.append("..")
from utils import (
    DATA_PATH,
    d_sl,
    dense_vegetation,
    modis_folder,
    modis_files,
    version,
)
from produce_maps.tcrit import Tcrit_map
from tqdm import tqdm
from os.path import join, basename


def get_exceeding_map(ext, sl, year="2001"):
    data_species_ = np.zeros(Tcrit_map[sl].shape) - 1000
    modis_files_ = [i for i in modis_files if f"/{year}" in i]
    for i, modis_file in tqdm(enumerate(modis_files_), total=len(modis_files_)):
        modis = rio.open(
            join(modis_folder, basename(modis_file)), "r"
        )
        m = modis.read(1)
        quant_inf = m < np.nanquantile(m, 0.01)
        m[m > np.nanquantile(m, 0.99)] = np.nan
        m[quant_inf] = np.nan
        m[dense_vegetation == 0] = np.nan
        data_species_ = np.nanmax(np.stack([m[sl], data_species_], axis=0), axis=0)
    data_species_[data_species_ == -1000] = np.nan
    ssps = (
        ["1981_2010"]
        if year == "2001"
        else ["1981_2010", "2041_2070_ssp370", "2071_2100_ssp370"]
    )
    for ssp in ssps:
        Tcrit = rio.open(
            DATA_PATH + f"/outputs/Tcrit_map_min_{ssp}{version}.tif", "r"
        ).read(1)
        Tcrit[Tcrit == 1000] = np.nan
        Tcrit[Tcrit == 0] = np.nan

        data = Tcrit[sl] - data_species_
        np.save(
            DATA_PATH
            + f"/outputs/deltaTcrit_Tmodis{ext}_{year}_tcrit{ssp}{version}.npy",
            data,
        )


for year in ["2001", "2020"]:
    for key, sl in d_sl.items():
        get_exceeding_map(key, sl, year)
