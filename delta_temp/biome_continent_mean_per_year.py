"""
Compute TSM quantiles per continent
"""
import sys
sys.path.append('..')
from tcrit import TCRIT, Tcrit_map, data_both_biomes
from utils import d_sl, weighted_quantile, compute_weights_lon, rio, np, modis_files, join, basename, interpolated_modis_folder, dense_vegetation
from tqdm import tqdm
from os.path import exists
import pickle
years = [str(i) for i in range(2001, 2021)]



for ext, sl in d_sl.items():
    Tcrit = Tcrit_map[sl]
    data_biomes = data_both_biomes[sl]

    def f():
        if TCRIT == "min":
            aa = ''
        elif TCRIT == "mean":
            aa = '_Tcritmean'
        elif TCRIT == "max":
            aa = '_Tcritmax'
        outfile = f'/home/gaston/Projects/EcoStress/images/biomes/MeanDeltaT_min_max_removal_biomes_{"_".join(years)}_{ext}_{aa}_maxperpixel_nanmax_fixed_allquantiles_tminv9_noterra_weightedquantiles__.pkl' #  tcriterra {ssp}
        if exists(outfile) and False:
            with open(outfile, 'rb') as file:
                d_hansen_temp = pickle.load(file)
            return d_hansen_temp
        d_hansen_temp_all = {b: {i: [] for i in range(len(modis_files))} for b in ["mean", "std", "0.9", "0.95", "0.99", "median", '0.1', '0.2', '0.3', '0.4', '0.6', '0.7', '0.8']}
        for i, modis_file in tqdm(enumerate(modis_files), total=len(modis_files)):
            if i % 12 == 0:
                data_species = np.zeros_like(Tcrit) - 1000
            interpolated_modis = rio.open(join(interpolated_modis_folder, basename(modis_file)), 'r')
            m = interpolated_modis.read(1)
            quant_inf = m < np.nanquantile(m, 0.01)
            m[m > np.nanquantile(m, 0.99)] = np.nan
            m[quant_inf] = np.nan
            m[dense_vegetation == 0] = np.nan
            data_species_ = (m[sl] - Tcrit)
            data_species = np.nanmax(np.stack([data_species_, data_species], axis=0), axis=0)
            if i % 12 == 11:
                data_species[data_species == -1000] = np.nan

                values = data_species[np.where(data_biomes)]
                weights_lon = compute_weights_lon(sl)
                weights_lon = weights_lon[np.where(data_biomes)]
                weights_lon = weights_lon[~np.isnan(values)]
                values = values[~np.isnan(values)]
                d_hansen_temp_all["mean"][i].append(np.nanmean(values))
                d_hansen_temp_all["std"][i].append(np.nanstd(values))
                d_hansen_temp_all["median"][i].append(weighted_quantile(values, 0.5, weights_lon))
                d_hansen_temp_all["0.6"][i].append(weighted_quantile(values, 0.6, weights_lon))
                d_hansen_temp_all["0.7"][i].append(weighted_quantile(values, 0.7, weights_lon))
                d_hansen_temp_all["0.8"][i].append(weighted_quantile(values, 0.8, weights_lon))
                d_hansen_temp_all["0.4"][i].append(weighted_quantile(values, 0.4, weights_lon))
                d_hansen_temp_all["0.3"][i].append(weighted_quantile(values, 0.3, weights_lon))
                d_hansen_temp_all["0.2"][i].append(weighted_quantile(values, 0.2, weights_lon))
                d_hansen_temp_all["0.1"][i].append(weighted_quantile(values, 0.1, weights_lon))
                d_hansen_temp_all["0.9"][i].append(weighted_quantile(values, 0.9, weights_lon))
                d_hansen_temp_all["0.95"][i].append(weighted_quantile(values, 0.95, weights_lon))
                d_hansen_temp_all["0.99"][i].append(weighted_quantile(values, 0.99, weights_lon))


        with open(outfile, 'wb') as file:
            pickle.dump(d_hansen_temp_all, file)

        with open(outfile, 'rb') as file:
            d_hansen_temp = pickle.load(file)
        return d_hansen_temp

    d_hansen_temp = f()