This code is associated with the Nature Plants submission **"Tropical forests are nearing critical temperature limits"**.

-  **delta_temp**: code used to output the TSM maps and the map of the directing coefficients of linear regressions at each pixel (slope.py). Also, compute the TSM variations by quantile (biome_continent_mean_per_year.py).
-  **produce_maps**: code used to output the critical temperature maps, maps of the number of species present per pixel, the skewness map, and the TSM maps projected in the future.

To avoid re-downloading all the data (especially MODIS data and species distribution maps), here's a link to get:
- the outputs of all the scripts in **produce_maps** and in **delta_temp**;
- the two maps used for dense vegetation filtering (LAI based and worldcover map (plant fraction) based);
- the future temperature maps;
- a *terraaqua.tif* file used only for visualization to distinguish land from water;
- the dataset resulting from the combination of the critical temperature datasets used (shared_species.csv);
- the rasters defining the biomes (folder *Ecoregions2017*).

With these data, the notebooks in *notebooks_figures* can be used to reproduce the figures presented in the article.

