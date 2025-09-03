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
    geo_slices,
    slice_tropics,
    modis_files,
    modis_folder,
    dense_vegetation
)

mean_tcrit_map = rio.open(DATA_PATH + f"/outputs/Tcrit_map_mean_1981_2010{version}.tif", "r").read(1)
min_tcrit_map = rio.open(DATA_PATH + f"/outputs/Tcrit_map_min_1981_2010{version}.tif", "r").read(1)

data_both_biomes = np.zeros(mean_tcrit_map.shape, dtype=bool)
biomes = [
    "Tropical & Subtropical Moist Broadleaf Forests",
    "Tropical & Subtropical Dry Broadleaf Forests",
]
biome_files = [join(DATA_PATH, f"Ecoregions2017/{b}.tif") for b in biomes]
for biome_file in biome_files:
    data_biome = rio.open(biome_file, "r").read(1).squeeze()
    data_biome = data_biome.astype(bool)
    data_both_biomes += data_biome

for continent, slice in geo_slices.items():
    print(continent)
    tcrit_slice = mean_tcrit_map[slice]

    outfile = (DATA_PATH + f"/outputs/TSM_2001_2020_{continent}_{version}.npy")
    if not exists(outfile):
        print(f"Computing TSM for {continent}")
        tsm = np.zeros((*tcrit_slice.shape, 20), dtype=np.float16) 
        tsm[:,:] = np.nan
        for i, modis_file in tqdm(enumerate(modis_files), total=len(modis_files)):
            with rio.open(join(modis_folder, basename(modis_file)), "r") as src:
                m = src.read(1)
                m[dense_vegetation == 0] = np.nan
                m[~data_both_biomes] = np.nan
                m[m == -1000] = np.nan
                m = m[slice]
                tsm[..., i] = tcrit_slice - m
        np.save(outfile, tsm)
    else:
        tsm = np.load(outfile)

    lr_outfile = (DATA_PATH + f"/outputs/LinearRegression_TSM_2001_2020_{continent}_{version}.npy")    
    if not exists(lr_outfile):
        print(f"Computing TSM Linear Regression for {continent}")
        X = np.arange(20).reshape(-1, 1)
        tsm_lr = np.zeros(tcrit_slice.shape)
        for i in tqdm(range(tsm_lr.shape[0]), total=tsm_lr.shape[0]):
            for j in range(tsm_lr.shape[1]):
                model = LinearRegression()
                x = X.copy()
                y = tsm[i, j].copy()
                nans = np.isnan(y)
                x = x[~nans]
                if not x.size:
                    tsm_lr[i, j] = np.nan
                else:
                    y = y[~nans]
                    model.fit(x.reshape(-1, 1), y.reshape(-1, 1))
                    tsm_lr[i, j] = model.coef_[0][0]
        np.save(lr_outfile, tsm_lr)
    
    tsm_min_tcrit_outfile = (DATA_PATH + f"/outputs/TSM_minTcrit_2001_2020_{continent}_{version}.npy")
    if not exists(tsm_min_tcrit_outfile):
        print(f"Computing TSM with min Tcrit for {continent}")
        min_tcrit_slice = min_tcrit_map[slice]
        min_tsm = np.zeros((*min_tcrit_slice.shape, 20), dtype=np.float16) 
        min_tsm[:,:] = np.nan
        for i, modis_file in tqdm(enumerate(modis_files), total=len(modis_files)):
            with rio.open(join(modis_folder, basename(modis_file)), "r") as src:
                m = src.read(1)
                m[dense_vegetation == 0] = np.nan
                m[~data_both_biomes] = np.nan
                m[m == -1000] = np.nan
                m = m[slice]
                min_tsm[..., i] = min_tcrit_slice - m
        np.save(tsm_min_tcrit_outfile, min_tsm)
        
# print(f"Merging TSM maps")
# tsm_2020_map = np.zeros_like(data_both_biomes).astype(float)
# tsm_2020_map[:,:] = np.nan
# for continent, slice in geo_slices.items():        
#     tsm_file = DATA_PATH + f"/outputs/TSM_2001_2020_{continent}_{version}.npy"
#     tsm_2020 = np.load(tsm_file)[...,-1]
#     tsm_2020_map[slice] = tsm_2020
# tsm_2020_map =  tsm_2020_map[slice_tropics]
# np.save(DATA_PATH + f"/outputs/TSM_2020{version}.npy", tsm_2020_map)

# print(f"Merging TSM Linear Regression maps")
# lr_2001_2020_map = np.zeros_like(data_both_biomes).astype(float)
# lr_2001_2020_map[:,:] = np.nan
# for continent, slice in geo_slices.items():        
#     lr_file = DATA_PATH + f"/outputs/LinearRegression_TSM_2001_2020_{continent}_{version}.npy"
#     lr = np.load(lr_file)
#     lr_2001_2020_map[slice] = lr
# lr_2001_2020_map =  lr_2001_2020_map[slice_tropics]
# np.save(DATA_PATH + f"/outputs/LinearRegression_TSM_2001_2020{version}.npy", lr_2001_2020_map)


