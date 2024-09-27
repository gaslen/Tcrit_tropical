import rasterio as rio 
import numpy as np
from os.path import join, expanduser, exists, basename
from os import listdir, system, makedirs
from rasterio.windows import Window, from_bounds
from shapely.geometry import box
from icecream import ic
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from glob import glob
from rasterio.plot import show, show_hist
from matplotlib import pyplot
from rasterio.mask import mask
import cv2 as cv


import sys
sys.path.append('..')
from utils import ssp, scale_img, modis_files, path_species, df, list_species


if __name__ == "__main__":
    modis_shape = rio.open(modis_files[0], 'r').shape
    meta = rio.open(modis_files[0], 'r').meta
    meta.update(compress="LZW")
    total_count = np.zeros(modis_shape, dtype=np.uint8)
    for i, sp in enumerate(tqdm(list_species, total=len(list_species))):
        threshold_temp = float(min(df[df['Plant species clean'] == sp]['Thermal Tolerance_deg.C']))
        merged_sp = join(path_species, sp)
        sdm_1980 = rio.open(join(merged_sp, f'{sp}_covariates_{ssp}.tif'), 'r')
        scaled_sdm_1980, window_sdm_1980 = scale_img(join(merged_sp, f'{sp}_covariates_{ssp}.tif'), modis_files[0])
        sp_map = np.zeros(modis_shape, dtype=bool)
        sdm_1980_int_slice = (
            slice(round(window_sdm_1980[0].start), round(window_sdm_1980[0].stop), None),
            slice(round(window_sdm_1980[1].start), round(window_sdm_1980[1].stop), None)
        )
        sp_map[sdm_1980_int_slice] = scaled_sdm_1980
        total_count += sp_map.astype(bool).astype(np.uint8)
    with rio.open(f'/data/gaston/ecostress/ecostress/worldwide/species_above_threshold_{ssp}.tif', 'w', **meta) as f:
        f.write(total_count, indexes=1)