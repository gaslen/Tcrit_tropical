import sys

sys.path.append("..")
import numpy as np
from produce_maps.tcrit import Tcrit_map, data_both_biomes
from utils import d_sl, list_species, df, version, DATA_PATH

from scipy.stats import skew
from tqdm import tqdm
from os.path import exists

d_ext = {
    "South America": "south_america",
    "Africa": "africa",
    "SE Asia": "south_east_asia",
}
d_ext = {value: key for key, value in d_ext.items()}


def compute_skewness(data, threshold_temps, outfile=None):
    threshold_temps_array = np.asarray(threshold_temps)
    expanded_thresholds = threshold_temps_array[np.newaxis, np.newaxis, :]
    masked_values = np.where(data, expanded_thresholds, np.nan)
    result = np.apply_along_axis(
        lambda x: skew(x, nan_policy="omit"), axis=-1, arr=masked_values
    )
    if outfile is not None:
        np.save(outfile, result)
    return result


for key, sl in tqdm(d_sl.items(), total=3):
    outfile = DATA_PATH + f"/outputs/species_presences_skewness{key}{version}.npy"
    if exists(outfile):
        continue
    ext = d_ext[key]
    Tmap_file = (
        DATA_PATH
        + f"/outputs/delta_Tmin_Tmodis{key}_per_year_2001_2020_reversed{version}.npy"
    )
    Tmap = np.load(Tmap_file) + Tcrit_map[sl][..., np.newaxis]
    Tmap = Tmap.astype(float)
    Tmap[~data_both_biomes[sl]] = np.nan
    Tmap2020 = Tmap[..., -1]
    Tmap = Tmap[..., 0]  # 2001

    data = np.load(
        DATA_PATH
        + f"/outputs/species_presences_{key}_covariates_1981_2010{version}.npy"
    )
    data[~data_both_biomes[sl]] = False
    data[np.isnan(Tmap)] = False
    z_sum = np.sum(data, axis=(0, 1))
    condition_species1 = np.where(z_sum != 0)[0]
    data = data[..., condition_species1]

    threshold_temps_ = []
    for sp in list_species:
        threshold_temps_.append(
            float(min(df[df["Plant species clean"] == sp]["Thermal Tolerance_deg.C"]))
        )
    threshold_temps = [threshold_temps_[i] for i in condition_species1]

    data_ = data.copy()

    condition_skewness = np.where(np.sum(data_, axis=2) > 2)  # because when ==2, => 0
    if not exists(outfile):
        skew_map_values = compute_skewness(
            data_[condition_skewness[0], condition_skewness[1]],
            threshold_temps,
            outfile,
        )

print("Compute entire map")
skew_map_tropics = np.full(data_both_biomes.shape, np.nan)

for key, sl in d_sl.items():
    ext = d_ext[key]
    Tmap_file = (
        DATA_PATH
        + f"/outputs/delta_Tmin_Tmodis{key}_per_year_2001_2020_reversed{version}.npy"
    )
    Tmap = np.load(Tmap_file) + Tcrit_map[sl][..., np.newaxis]
    Tmap = Tmap.astype(float)
    Tmap[~data_both_biomes[sl]] = np.nan
    Tmap = Tmap[..., 0]
    data = np.load(
        DATA_PATH
        + f"/outputs/species_presences_{key}_covariates_1981_2010{version}.npy"
    )
    data[~data_both_biomes[sl]] = False
    data[np.isnan(Tmap)] = False
    z_sum = np.sum(data, axis=(0, 1))
    condition_species1 = np.where(z_sum != 0)[0]
    data = data[..., condition_species1]

    threshold_temps_ = []
    for sp in list_species:
        threshold_temps_.append(
            float(min(df[df["Plant species clean"] == sp]["Thermal Tolerance_deg.C"]))
        )
    threshold_temps = [threshold_temps_[i] for i in condition_species1]

    condition_skewness = np.where(np.sum(data, axis=2) > 2)  # because when ==2, => 0

    outfile = DATA_PATH + f"/outputs/species_presences_skewness{key}{version}.npy"
    skew_map_values = np.load(outfile)
    skew_map = np.full(data.shape[:-1], np.nan)

    skew_map[condition_skewness] = skew_map_values
    skew_map[np.sum(data, axis=-1) == 2] = 0
    skew_map[np.sum(data, axis=-1) == 1] = 0
    skew_map_tropics[sl] = skew_map
np.save(
    DATA_PATH + f"/outputs/species_presences_skewness_tropics{version}.npy",
    skew_map_tropics,
)
