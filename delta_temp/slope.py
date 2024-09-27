"""
Compute TSM map and linear regression coefficients map
"""
import sys
sys.path.append('..')
from utils import d_sl, rio, np, modis_files, interpolated_modis_folder, dense_vegetation, years
from sklearn.linear_model import LinearRegression
from tcrit import Tcrit_map
from os.path import exists, join, basename
from tqdm import tqdm



for ext, sl in d_sl.items():
    outfile = f"/data/gaston/ecostress/ecostress/worldwide/delta_Tmin_Tmodis{ext}_per_year_2001_2020_reversed_tminv6.npy"
    lr_outfile = f"/data/gaston/ecostress/ecostress/worldwide/LinearRegression_delta_Tmin_Tmodis{ext}_per_year_2001_2020_tminv6.npy"
    

    Tcrit = Tcrit_map[sl]

    if not exists(outfile) or True:
        out = np.zeros((*Tcrit.shape, 20), dtype=np.float16) - 1000
        for i, modis_file in tqdm(enumerate(modis_files), total=len(modis_files)):
            j = i // 12
            interpolated_modis = rio.open(join(interpolated_modis_folder, basename(modis_file)), 'r')
            m = interpolated_modis.read(1)
            quant_inf = m < np.nanquantile(m, 0.01)
            m[m > np.nanquantile(m, 0.99)] = np.nan
            m[quant_inf] = np.nan
            m[dense_vegetation == 0] = np.nan
            m = m[sl]
            data_species = (m - Tcrit)
            data_species[data_species == 0] = np.nan 
            out[..., j] = np.nanmax(np.stack([data_species, out[..., j]], axis=0), axis=0)
        out[out==-1000] = np.nan
        np.save(outfile, out)
        
    if not exists(lr_outfile) or True:
        X = np.arange(20).reshape(-1, 1)
        map = np.load(outfile)
        map_ = (map + Tcrit[..., np.newaxis]) 
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