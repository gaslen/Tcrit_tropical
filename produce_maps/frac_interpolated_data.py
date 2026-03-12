import rasterio as rio
import numpy as np
import pandas as pd
from glob import glob
from os.path import join
import sys
sys.path.append("..")

from utils import (
    DATA_PATH,
    modis_files,
    geo_slices,
    dense_vegetation,
    version
)

out_path = (DATA_PATH + f"/outputs/frac_interpolated_pixels_modis{version}.csv") 

mean_tcrit_map = rio.open(DATA_PATH + f"/outputs/Tcrit_map_mean_1981_2010{version}.tif", "r").read(1)
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

# interpolated modis data only in study area (use first file)
m_int = rio.open(modis_files[0]).read(1)
m_int[data_both_biomes == 0] = np.nan
m_int[dense_vegetation == 0] = np.nan
m_int[m_int == -1000] = np.nan

# mask where data is considered in interpolated modis data
data_available = ~np.isnan(m_int)

# get paths to raw, uninterpolated modis data
raw_modis_files = sorted(glob(join(DATA_PATH + '/Modis_fixed_scale_and_nans_with_clean_preprocessing', "*.tif")))

# Build list of records for output dataframe
records = []
for y in np.arange(2001, 2021, 1):
    print(y)
    raw_modis_files_year = [rm for rm in raw_modis_files if rm.split('/')[-1].split('-')[0] == str(y)]
    assert len(raw_modis_files_year) == 12

    for rm in raw_modis_files_year:
        month = int(rm.split('/')[-1].split('-')[1])
        m_raw = rio.open(rm).read(1)
        
        # Calculate for total
        frac_total = (np.sum(m_raw[data_available] == 0)/m_raw[data_available].shape[0]) * 100
        
        # Calculate for each continent
        frac_continents = {}
        for continent, slice in geo_slices.items():
            m_int_slice = m_int[slice]
            m_raw_slice = m_raw[slice]
            data_available_slice = ~np.isnan(m_int_slice)
            frac = (np.sum(m_raw_slice[data_available_slice] == 0)/m_raw_slice[data_available_slice].shape[0]) * 100
            frac_continents[continent] = frac
        
        # Add record
        records.append({
            'year': y,
            'month': month,
            'total': frac_total,
            'SA': frac_continents['south_america'],
            'SEA': frac_continents['south_east_asia'],
            'Africa': frac_continents['africa']
        })

# Create dataframe
df_frac_interpolated = pd.DataFrame(records)
df_frac_interpolated.to_csv(out_path, index=False)
print(f"Saved to {out_path}")
