This code is associated with the Nature Communications submission **"Tropical forests are nearing critical temperature limits"**.

# Folder contents
-  **delta_temp**: code used to output the TSM maps and the map of the directing coefficients of linear regressions at each pixel (slope.py). Also, compute the TSM variations by quantile (biome_continent_mean_per_year.py).
-  **produce_maps**: code used to output the critical temperature maps, maps of the number of species present per pixel, the skewness map, and the TSM maps projected in the future.
-  **notebooks_figures**: reproduce the figures presented in the article using the outputs of the two other folders.

# Data
To avoid re-downloading all the data (especially MODIS data and the species distribution maps), you can find [here](https://drive.google.com/drive/folders/1yjFI9VdnGWl4enQxDJJ9foj2wdffg8QP?usp=sharing):
- the outputs of all the scripts in **produce_maps** and in **delta_temp**;
- the two maps used for dense vegetation filtering (LAI based and worldcover map (plant fraction) based);
- the future temperature maps;
- a *terraaqua.tif* file used only for visualization to distinguish land from water;
- the dataset resulting from the combination of the critical temperature datasets used (shared_species.csv);
- the rasters defining the biomes (folder *Ecoregions2017*).
