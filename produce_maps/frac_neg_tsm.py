import rasterio as rio
import numpy as np
from tqdm import tqdm
from os.path import join, exists

import sys
sys.path.append("..")
from utils import (
    DATA_PATH,
    version,
    list_species, 
    species_df, 
    path_sdms, 
    scale_img,
    shape_full_map,
    modis_folder,
    dense_vegetation,
    geo_slices,
    slice_tropics
)

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

for year in ['2001', '2020', '2050', '2100']:
    print(year)
    modis_file = "2020.tif" if year == '2050' or year == '2100' else f"{year}.tif"
    with rio.open(join(modis_folder,modis_file), "r") as src:
        m = src.read(1)
        m[dense_vegetation == 0] = np.nan
        m[~data_both_biomes] = np.nan
        m[m == -1000] = np.nan

    for continent, sl in geo_slices.items():
        print(continent)
        outfile_sps_counts = (DATA_PATH + f"/outputs/species_counts_map_{continent}_{year}{version}.npy")
        outfile_sps_neg_tsm_counts = (DATA_PATH + f"/outputs/species_negative_tsm_counts_map_{continent}_{year}{version}.npy")
        if year == '2050' or year == '2100':
            outfile_sps_neg_tsm_acclim_counts = (DATA_PATH + f"/outputs/species_negative_tsm_counts_acclim_map_{continent}_{year}{version}.npy")

        if (not exists(outfile_sps_counts)) | (not exists(outfile_sps_neg_tsm_counts)):
            m_slice = m[sl]
            if year == '2050' or year == '2100':
                delta_tsurf = rio.open(DATA_PATH + f"/2050-2100_temperatures/delta_tsurf_2020_{year}.tif", 'r').read(1)
                m_slice += delta_tsurf[sl]

            sps_counts = np.zeros(m_slice.shape)
            sps_neg_tsm_counts = np.zeros(m_slice.shape)
            if year == '2050' or year == '2100':
                sps_neg_tsm_acclim_counts = np.zeros(m_slice.shape)

            for sp in tqdm(list_species, total=len(list_species)):
                sp_tcrit = float(np.mean(species_df[species_df["Plant species clean"] == sp]["Thermal Tolerance_deg.C"]))
                sdm, window_sdm = scale_img(join(path_sdms, sp, f"{sp}_covariates_1981_2010.tif"), 
                                            DATA_PATH + "/dense_vegetation/plant_fraction_LST_Day.tif")
                sp_map = np.zeros(shape_full_map)
                sdm_int_slice = (slice(round(window_sdm[0].start),round(window_sdm[0].stop),None,),
                                slice(round(window_sdm[1].start),round(window_sdm[1].stop),None,))
                sp_map[sdm_int_slice] = sdm
                sp_map = sp_map[sl]
                sp_map[np.where(np.isnan(m_slice))] = np.nan
                sp_map = np.where(sp_map == 1, 1, np.nan)

                sps_counts += np.where(sp_map == 1, 1, 0)
                sps_neg_tsm_counts += np.where((sp_tcrit*sp_map <= m_slice), 1, 0)
                if year == '2050' or year == '2100':
                    sps_neg_tsm_acclim_counts += np.where((sp_tcrit*sp_map + (delta_tsurf[sl]*0.38) <= m), 1, 0)
            
            np.save(outfile_sps_counts, sps_counts)
            np.save(outfile_sps_neg_tsm_counts, sps_neg_tsm_counts)
            if year == '2050' or year == '2100':
                np.save(outfile_sps_neg_tsm_acclim_counts, sps_neg_tsm_acclim_counts)
            
            
