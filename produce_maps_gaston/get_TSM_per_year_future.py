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
from produce_maps.tcrit import Tcrit_map, TCRIT
from tqdm import tqdm
from os.path import join, basename


def get_exceeding_map(ext, sl, year="2001"):
    modis = rio.open(
        join(modis_folder, year + '.tif'), "r"
    )
    m = modis.read(1)
    m[dense_vegetation == 0] = np.nan
    m[m == -1000] = np.nan
    ssps = (
        ["1981_2010"]
        if year == "2001"
        else ["1981_2010", "2041_2070_ssp370", "2071_2100_ssp370"]
    )
    for ssp in ssps:
        Tcrit = rio.open(
            DATA_PATH + f"/outputs/Tcrit_map_{TCRIT}_{ssp}{version}.tif", "r"
        ).read(1)
        Tcrit[Tcrit == 1000] = np.nan
        Tcrit[Tcrit == 0] = np.nan

        data = Tcrit[sl] - m[sl]
        np.save(
            DATA_PATH
            + f"/outputs/deltaTcrit_Tmodis{ext}_{year}_tcrit{ssp}{version}.npy",
            data,
        )


for year in ["2001", "2020"]:
    for key, sl in d_sl.items():
        get_exceeding_map(key, sl, year)
