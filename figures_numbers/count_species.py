import numpy as np
import sys
sys.path.append('..')
from utils import ssp, d_sl, np, version, DATA_PATH

for key in d_sl.keys():
    # if key != 'africa':
    #     continue
    data = np.load(DATA_PATH + f"/outputs/species_presences_{key}_covariates_{ssp}{version}.npy")
    d=np.sum(data, axis=-1)
    print(key)
    print("mean", "max", np.mean(d[d>0]), np.max(d[d>0])) # mean number of species
    data = np.sum(data, axis=0)
    data = np.sum(data, axis=0)
    data = data > 0
    print("total number of species", np.sum(data))
# south_east_asia
# mean max 5.417132952815092 29
# total number of species 47
# south_america
# mean max 18.284833015384493 114
# total number of species 172
# africa
# mean max 2.5151223511423675 11
# total number of species 14