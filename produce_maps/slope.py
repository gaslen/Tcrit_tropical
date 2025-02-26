"""
Compute TSM map and linear regression coefficients map
"""

import sys

sys.path.append("..")
from utils import (
    d_sl,
    rio,
    np,
    modis_files,
    interpolated_modis_folder,
    dense_vegetation,
    ssp,
    version,
    DATA_PATH,
)
from sklearn.linear_model import LinearRegression
from tcrit import Tcrit_map, TCRIT
from os.path import exists, join, basename
from tqdm import tqdm


for ext, sl in d_sl.items():
    outfile = (
        DATA_PATH
        + f"/outputs/delta_T{TCRIT}_Tmodis{ext}_per_year_2001_2020_reversed{version}.npy"
    )  # _: v11, nothing: v10
    lr_outfile = (
        DATA_PATH
        + f"/outputs/LinearRegression_delta_T{TCRIT}_Tmodis{ext}_per_year_2001_2020{version}.npy"
    )

    Tcrit = Tcrit_map[sl]

    if not exists(outfile):
        out = np.zeros((*Tcrit.shape, 20), dtype=np.float16) - 1000
        for i, modis_file in tqdm(enumerate(modis_files), total=len(modis_files)):
            j = i // 12
            interpolated_modis = rio.open(
                join(interpolated_modis_folder, basename(modis_file)), "r"
            )
            m = interpolated_modis.read(1)
            quant_inf = m < np.nanquantile(m, 0.01)
            m[m > np.nanquantile(m, 0.99)] = np.nan
            m[quant_inf] = np.nan
            m[dense_vegetation == 0] = np.nan
            m = m[sl]
            data_species = m - Tcrit
            data_species[data_species == 0] = np.nan
            out[..., j] = np.nanmax(
                np.stack([data_species, out[..., j]], axis=0), axis=0
            )
        out[out == -1000] = np.nan
        np.save(outfile, out)

    if not exists(lr_outfile):
        X = np.arange(20).reshape(-1, 1)
        map = np.load(outfile)
        map_ = map + Tcrit[..., np.newaxis]
        new_map = np.zeros(Tcrit.shape)
        for i in tqdm(range(map.shape[0]), total=map.shape[0]):
            for j in tqdm(range(map.shape[1]), total=map.shape[1]):
                model = LinearRegression()
                x = X.copy()
                y = map[i, j].copy()
                nans = np.isnan(y)
                x = x[~nans]
                if not x.size:
                    new_map[i, j] = np.nan
                else:
                    y = y[~nans]
                    model.fit(x.reshape(-1, 1), y.reshape(-1, 1))
                    new_map[i, j] = model.coef_[0][0]
        np.save(lr_outfile, new_map)

# for the Tmax analysis in the Appendix
TCRIT = "max"

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

for ext, sl in d_sl.items():
    outfile = (
        DATA_PATH
        + f"/outputs/delta_T{TCRIT}_Tmodis{ext}_per_year_2001_2020_reversed{version}.npy"
    )  # _: v11, nothing: v10
    lr_outfile = (
        DATA_PATH
        + f"/outputs/LinearRegression_delta_T{TCRIT}_Tmodis{ext}_per_year_2001_2020{version}.npy"
    )

    Tcrit = Tcrit_map[sl]

    if not exists(outfile):
        out = np.zeros((*Tcrit.shape, 20), dtype=np.float16) - 1000
        for i, modis_file in tqdm(enumerate(modis_files), total=len(modis_files)):
            j = i // 12
            interpolated_modis = rio.open(
                join(interpolated_modis_folder, basename(modis_file)), "r"
            )
            m = interpolated_modis.read(1)
            quant_inf = m < np.nanquantile(m, 0.01)
            m[m > np.nanquantile(m, 0.99)] = np.nan
            m[quant_inf] = np.nan
            m[dense_vegetation == 0] = np.nan
            m = m[sl]
            data_species = m - Tcrit
            data_species[data_species == 0] = np.nan
            out[..., j] = np.nanmax(
                np.stack([data_species, out[..., j]], axis=0), axis=0
            )
        out[out == -1000] = np.nan
        np.save(outfile, out)
