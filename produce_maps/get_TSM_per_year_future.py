import numpy as np
import rasterio as rio
import sys
sys.path.append('..')
from utils import d_sl, years, dense_vegetation, sl_tropics, interpolated_modis_folder, modis_files
from delta_temp.tcrit import TCRIT, Tcrit_map, data_both_biomes
from tqdm import tqdm 
from os.path import join, basename
import matplotlib.pyplot as plt
import seaborn as sns

def get_exceeding_map(ext, sl, year='2001'):
    data_species_ = np.zeros(Tcrit_map[sl].shape) - 1000
    modis_files_ = [i for i in modis_files if f'/{year}' in i]
    for i, modis_file in tqdm(enumerate(modis_files_), total=len(modis_files_)):
        interpolated_modis = rio.open(join(interpolated_modis_folder, basename(modis_file)), 'r')
        m = interpolated_modis.read(1)
        m[dense_vegetation == 0] = np.nan
        quant_inf = m < np.nanquantile(m, 0.01)
        m[m > np.nanquantile(m, 0.99)] = np.nan
        m[quant_inf] = np.nan
        data_species_ = np.nanmax(np.stack([m[sl], data_species_], axis=0), axis=0)
    data_species_[data_species_ == -1000] = np.nan
    ssps = ['1981_2010'] if year == '2001' else ['1981_2010', '2041_2070_ssp370', '2071_2100_ssp370']
    for ssp in ssps:
        Tcrit = rio.open(f"/data/gaston/ecostress/ecostress/worldwide/Tcrit_map_min_{ssp}.tif", 'r').read(1)
        Tcrit[Tcrit==1000] = np.nan
        Tcrit[Tcrit==0] = np.nan
        
        data = Tcrit[sl] - data_species_
        np.save(f"/data/gaston/ecostress/ecostress/worldwide/deltaTcrit_Tmodis{ext}_{year}_tcrit{ssp}.npy", data)

for year in ['2001', '2020']:
    print(year)
    for key, sl in d_sl.items():
        print(key)
        get_exceeding_map(key, sl, year)