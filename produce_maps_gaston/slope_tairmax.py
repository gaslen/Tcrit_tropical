import sys

sys.path.append("..")
import numpy as np
import rasterio as rio
from os.path import basename, exists
from tqdm import tqdm
from utils import d_sl, version, modis_files, DATA_PATH
from sklearn.linear_model import LinearRegression


Tcrit_map = rio.open(
    DATA_PATH + f"/outputs/Tcrit_map_max_1981_2010{version}.tif", "r"
).read(1)
Tcrit_map[Tcrit_map == 0] = np.nan

for ext, sl in d_sl.items():
    outfile = (
        DATA_PATH + f"/outputs/Tair{ext}_per_year_2001_2020_reversed_{version}.npy"
    )
    lr_outfile = (
        DATA_PATH
        + f"/outputs/LinearRegression_Tair{ext}_per_year_2001_2020_{version}.npy"
    )
    if not exists(outfile):
        out = np.zeros((*Tcrit_map[sl].shape, 20), dtype=np.float16) - 1000
        modis_files = [
            i
            for i in modis_files
            if not basename(i).startswith("2021") and not basename(i).startswith("2022")
        ]
        for i, modis_file in tqdm(enumerate(modis_files), total=len(modis_files)):
            j = i // 12
            if i % 12 == 11:
                tair = np.load(
                    DATA_PATH + f"/ERAdataperyear/{ext}/{str(2001+j)}_maxtair.npy"
                )
                tair[np.isnan(out[..., j])] = np.nan
                out[..., j] = tair
        out[out == -1000] = np.nan
        np.save(outfile, out)
    if not exists(lr_outfile):
        X = np.arange(20).reshape(-1, 1)
        map = np.load(outfile)
        map_ = map + Tcrit_map[sl][..., np.newaxis]
        new_map = np.zeros(Tcrit_map[sl].shape)
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
                    new_map[i, j] = model.coef_[0]
        np.save(lr_outfile, new_map)
