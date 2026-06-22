# **Tropical forests are facing increasing risks of exposure to critical temperature thresholds**

This repository contains the code associated with the paper **"Tropical forests are facing increasing risks of exposure to critical temperature thresholds"**.

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
  - **`species_negative_tsm_counts.py`**: generates maps of total species counts and counts of species with negative TSM values
  - **`TSM_future.py`**: generates TSM maps for future projections 

- **Figures and numbers generation:**  
  All figures are made in the **`figures.ipynb`** notebook.

---

