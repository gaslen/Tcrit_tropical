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
from utils import scale_img, d_sl, modis_files, path_species, list_species, ssp
from utils import df as df_species



if __name__ == "__main__":
    for key, sl in d_sl.items():
        modis_shape = rio.open(modis_files[0], 'r').shape
        final_shape = rio.open(modis_files[0], 'r').read(1)[sl].shape
        species_map = np.zeros((*final_shape, len(list_species)), dtype=bool)
        for counter, sp in enumerate(tqdm(list_species, total=len(list_species))):
            threshold_temp = float(min(df_species[df_species['Plant species clean'] == sp]['Thermal Tolerance_deg.C']))
            merged_sp = join(path_species, sp)
            scaled_sdm_1980, window_sdm_1980 = scale_img(join(merged_sp, f'{sp}_covariates_{ssp}.tif'), modis_files[0])
            sp_map = np.zeros(modis_shape, dtype=bool)
            
            sdm_1980_int_slice = (
                slice(round(window_sdm_1980[0].start), round(window_sdm_1980[0].stop), None),
                slice(round(window_sdm_1980[1].start), round(window_sdm_1980[1].stop), None)
            )
            
            sp_map[sdm_1980_int_slice] = scaled_sdm_1980
            processed_sp_map = sp_map[sl]
            species_map[..., counter] = processed_sp_map.astype(bool)

        np.save(f"/data/gaston/ecostress/ecostress/worldwide/species_presences_{key}_covariates_{ssp}.npy", species_map)