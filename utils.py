import rasterio as rio
import numpy as np
from os.path import join, expanduser, basename
from rasterio.windows import from_bounds
from shapely.geometry import box
import pandas as pd
from glob import glob
import colorsys
from merge_Tcrits_datasets import DATA_PATH, version


ssp = "1981_2010"  # 1981_2010 2071_2100_ssp370  2041_2070_ssp370
years = [str(i) for i in range(2001, 2021)]


d_sl = {
    "south_east_asia": (slice(6861, 11879, None), slice(30199, 40198, None)),
    "south_america": (slice(6961, 14065, None), slice(8300, 17422, None)),
    "africa": (slice(9148, 13645, None), slice(19962, 27655, None)),
}

sl_tropics = np.index_exp[6861:14655, 8000:40198]


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


def cast_small_in_large(large_rio_dataset, small_rio_dataset, value=np.nan):
    window = from_bounds(
        *large_rio_dataset.bounds, large_rio_dataset.transform
    ).intersection(from_bounds(*small_rio_dataset.bounds, small_rio_dataset.transform))
    small_data = small_rio_dataset.read(window=window)
    window = window.toslices()
    sp_map = np.zeros(large_rio_dataset.shape) + value
    sdm_1980_int_slice = (
        slice(round(window[0].start), round(window[0].stop), None),
        slice(round(window[1].start), round(window[1].stop), None),
    )
    sp_map[sdm_1980_int_slice] = small_data
    return sp_map


def random_colors(n, bright=True):
    """
    Generate random colors.
    To get visually distinct colors, generate them in HSV space then
    convert to RGB.
    """
    hsv = [(i / n, 1, 0.5 + 0.5 * (i % 2 == 0)) for i in range(n)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    return colors


def bbox(img):
    rows = np.any(img, axis=1)
    cols = np.any(img, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return np.index_exp[rmin:rmax, cmin:cmax]


def K_to_C(t):
    return t * 0.02 - 273.15


df = pd.read_csv(
    DATA_PATH + f"/data_species/shared_species{version}.csv"
)  # v2: Toutes les Tmax, v3 seulemnt les Tcrit de Lancaster, v4 Tmax et Tcrit Lancaster, v6: Tcrit, T50, Sullivan  # v7: remove sullivan and Lancaster T50. Only Tcrit from Lancaster and Slot. v8: Re-add Sullivan
min_threshold_temp = float(min(df["Thermal Tolerance_deg.C"]))

path_species = expanduser(DATA_PATH + "/sdm_merged")
list_species = sorted(list(set(df["Plant species clean"].tolist())))

plant_fraction = rio.open(
    DATA_PATH + "/dense_vegetation/plant_fraction_LST_Day.tif", "r"
).read(1)
lai = rio.open(DATA_PATH + "/dense_vegetation/LAI.tif", "r").read(1)
lai = lai > 20
dense_vegetation = lai * plant_fraction

meta_full_map = rio.open(
    DATA_PATH + "/dense_vegetation/plant_fraction_LST_Day.tif", "r"
).meta
shape_full_map = rio.open(
    DATA_PATH + "/dense_vegetation/plant_fraction_LST_Day.tif", "r"
).shape

modis_folder = (
    DATA_PATH
    + "/MODIS_LST_Yearly"
)
modis_files = sorted(glob(join(modis_folder, "*.tif")))
modis_files = [
    i
    for i in modis_files
    if not basename(i).startswith("2021") and not basename(i).startswith("2022")
]
data_folder = "species_monthly"

distance_array = np.abs(np.arange(21122) - 21122 // 2)  # distance from ecuator


def compute_weights_lon(sl=None):
    src = rio.open(DATA_PATH + f"/outputs/Tcrit_map_mean_{ssp}{version}.tif", "r")
    res = src.res[0]
    shp = src.shape[1]
    weights = np.cos(np.radians(distance_array * res)) * 111320 * res
    weights /= np.max(weights)
    weights = np.repeat(weights[:, np.newaxis], shp, axis=1)
    return weights[sl]


# https://stackoverflow.com/questions/1253499/simple-calculations-for-working-with-lat-lon-and-km-distance
def compute_area_hectares(array, sl=None):
    res = rio.open(DATA_PATH + f"/outputs/Tcrit_map_min_{ssp}{version}.tif", "r").res[0]
    lon_meters = (np.cos(np.radians(distance_array * res)) * 111320 * res)[sl[0]]
    lat_meters = res * 110574
    return np.sum(lon_meters[np.where(array)[0]] * lat_meters / 10000)


def weighted_quantile(
    values, quantiles, sample_weight=None, values_sorted=False, old_style=False
):
    """source: https://stackoverflow.com/questions/21844024/weighted-percentile-using-numpy
    Very close to numpy.percentile, but supports weights.
    NOTE: quantiles should be in [0, 1]!
    :param values: numpy.array with data
    :param quantiles: array-like with many quantiles needed
    :param sample_weight: array-like of the same length as `array`
    :param values_sorted: bool, if True, then will avoid sorting of
        initial array
    :param old_style: if True, will correct output to be consistent
        with numpy.percentile.
    :return: numpy.array with computed quantiles.
    """
    values = np.array(values)
    quantiles = np.array(quantiles)
    if sample_weight is None:
        sample_weight = np.ones(len(values))
    sample_weight = np.array(sample_weight)
    assert np.all(quantiles >= 0) and np.all(
        quantiles <= 1
    ), "quantiles should be in [0, 1]"

    if not values_sorted:
        sorter = np.argsort(values)
        values = values[sorter]
        sample_weight = sample_weight[sorter]

    weighted_quantiles = np.cumsum(sample_weight) - 0.5 * sample_weight
    if old_style:
        # To be convenient with numpy.percentile
        weighted_quantiles -= weighted_quantiles[0]
        weighted_quantiles /= weighted_quantiles[-1]
    else:
        weighted_quantiles /= np.sum(sample_weight)
    return np.interp(quantiles, weighted_quantiles, values)
