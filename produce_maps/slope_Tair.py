import rasterio as rio
import numpy as np
from tqdm import tqdm
from os.path import join, basename, exists
from sklearn.linear_model import LinearRegression

import sys
sys.path.append("..")
from utils import (
    DATA_PATH,
    version,
    geo_slices
)

mean_tcrit_map = rio.open(DATA_PATH + f"/outputs/Tcrit_map_mean_1981_2010{version}.tif", "r").read(1)

for continent, slice in geo_slices.items():
    print(continent)

    outfile = (DATA_PATH + f"/outputs/Tair_2001_2020_{continent}{version}.npy")
    lr_outfile = (DATA_PATH + f"/outputs/LinearRegression_Tair_2001_2020_{continent}{version}.npy")

    if exists(outfile) and exists(lr_outfile):
        continue
    
    tcrit_slice = mean_tcrit_map[slice]
    out = np.zeros((*tcrit_slice.shape, 20), dtype=np.float16) - 1000
    for i, year in enumerate(np.arange(2001,2021,1)):
        print('\t', i, year)
        tair = np.load(DATA_PATH + f"/ERAdataperyear/{continent}/{year}_maxtair.npy")
        tair[np.isnan(out[..., i])] = np.nan
        out[..., i] = tair
    out[out == -1000] = np.nan
    np.save(outfile, out)

    if exists(lr_outfile):
        continue

    out = np.load(outfile)
    X = np.arange(20).reshape(-1, 1)
    lr_map = np.zeros_like(out[...,0], dtype=np.float16)
    for i in tqdm(range(out.shape[0]), total=out.shape[0]):
        for j in tqdm(range(out.shape[1]), total=out.shape[1]):
            if np.isnan(out[i,j,:]).all():
                lr_map[i,j] = np.nan
            else:
                x = X.copy()
                y = out[i,j,:].copy()
                nans = np.isnan(y)
                x = x[~nans]
                if not x.size:
                    lr_map[i,j] = np.nan
                else:                    
                    y = y[~nans]
                    lr = LinearRegression().fit(x, y)
                    lr_map[i,j] = lr.coef_[0]
    np.save(lr_outfile, lr_map)