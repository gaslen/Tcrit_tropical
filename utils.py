import rasterio as rio
import numpy as np
from os.path import join, expanduser, basename
from rasterio.windows import from_bounds
from shapely.geometry import box
import pandas as pd
from glob import glob
# import colorsys
from merge_Tcrits_datasets import DATA_PATH, version

geo_slices = {
    "south_east_asia": (slice(6861, 11879, None), slice(30199, 40198, None)),
    "south_america": (slice(6961, 14065, None), slice(8300, 17422, None)),
    "africa": (slice(9148, 13645, None), slice(19962, 27655, None)),
}
slice_tropics = np.index_exp[6861:14655, 8000:40198]

species_df = pd.read_csv(DATA_PATH + f"/data_species/shared_species{version}.csv")  
list_species = sorted(list(set(species_df["Plant species clean"].tolist())))
# min_threshold_temp = float(min(df["Thermal Tolerance_deg.C"]))

path_sdms = expanduser(DATA_PATH + "/sdm_merged")

plant_fraction = rio.open(DATA_PATH + "/dense_vegetation/plant_fraction_LST_Day.tif", "r").read(1)
lai = rio.open(DATA_PATH + "/dense_vegetation/LAI.tif", "r").read(1)
lai = lai > 20
dense_vegetation = lai * plant_fraction

meta_full_map = rio.open(
    DATA_PATH + "/dense_vegetation/plant_fraction_LST_Day.tif", "r"
).meta
shape_full_map = rio.open(
    DATA_PATH + "/dense_vegetation/plant_fraction_LST_Day.tif", "r"
).shape

# ssp = "1981_2010"  # 1981_2010 2071_2100_ssp370  2041_2070_ssp370
# years = [str(i) for i in range(2001, 2021)]

modis_folder = (DATA_PATH + "/MODIS_LST_Yearly")
modis_files = sorted(glob(join(modis_folder, "*.tif")))
modis_files = [i for i in modis_files if not basename(i).startswith("2021") and not basename(i).startswith("2022")]
# data_folder = "species_monthly"



def scale_img(img_file, support_file):
    """To align a tiff file to the same resolution than a support one"""
    img = rio.open(img_file, "r")
    support = rio.open(support_file, "r")
    x_scale = img.transform.a / support.transform.a
    y_scale = img.transform.e / support.transform.e
    imgbox = box(*img.bounds)
    support_box = box(*support.bounds)
    intersection = imgbox.intersection(support_box)
    window = from_bounds(*intersection.bounds, img.transform)
    original_window_slice = (
        from_bounds(*intersection.bounds, support.transform)
        .round_lengths()
        .round_offsets()
        .toslices()
    )
    out_shape = (round(window.height * y_scale), round(window.width * x_scale))
    img_data = img.read(
        window=window,
        out_shape=out_shape,
    )[0]
    return img_data, original_window_slice

# https://stackoverflow.com/questions/1253499/simple-calculations-for-working-with-lat-lon-and-km-distance
def compute_area_hectares(array, sl=None):
    distance_array = np.abs(np.arange(21122) - 21122 // 2)  # distance from ecuator
    res = rio.open(DATA_PATH + f"/outputs/Tcrit_map_mean_1981_2010{version}.tif", "r").res[0]
    lon_meters = (np.cos(np.radians(distance_array * res)) * 111320 * res)[sl[0]]
    lat_meters = res * 110574
    return np.sum(lon_meters[np.where(array)[0]] * lat_meters / 10000)

