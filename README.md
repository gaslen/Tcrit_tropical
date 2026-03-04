# **Tropical Forests Are Nearing Critical Temperature Limits**

This repository contains the code associated with the PNAS submission **"Tropical forests are nearing critical temperature limits"**.

### **Data Access**
- **Public Data:** All associated data (land surface temperatures, vegetation maps, SDMs outputs, air temperatures, Tcrit databases, ecoregions) will be accessed [here](https://zenodo.org/records/15083361). All the tar.gz archives should be extracted before use.

### **Setup**
To set up the Python environment, run:
```bash
conda create --name ecostress python=3.11
conda activate ecostress
pip install -r requirements.txt
```
:exclamation::exclamation::exclamation: Ensure the `DATA_PATH` in *merge_Tcrits_datasets.py* is set correctly to point to your local data directory.

---

### **Code Overview**

- **Data Preparation:**  
  **`merge_Tcrits_datasets.py`**: Merges the different Tcrit datasets.

- **Map Generation:**  
  The python scripts in the **`produce_maps`** folder generate the maps used in the figures and analysis.  
  - **`Tcrit.py`**: generates critical temperature maps  
  - **`TSM.py`**: generates TSM maps and linear regression coefficients per pixel  
  **`species_negative_tsm_counts.py`**: generates maps of total species counts and counts of species with negative TSM values
  - **`TSM_future.py`**: generates TSM maps for future projections 

- **Figures and numbers generation:**  
  All figures are made in the **`figures.ipynb`** notebook.
  <!-- The **`create_structure_figures_folders.py`** script create the structure of the folders used to save the figures. -->
  <!-- The **`figures_numbers`** scripts create figures and compute numbers for the paper. -->

---

