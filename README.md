# **Tropical Forests Are Nearing Critical Temperature Limits**

This repository contains the code associated with the PNAS submission **"Tropical forests are nearing critical temperature limits"**.

### **Data Access**
- **Public Data:** All associated data will be accessed [here](<link_to_data>).
- **ECEO Members:** Data is also available at:  
  ```
  eceosrv1_nas/Datasets/gaston/ecostress_data/
  ```

### **Setup**
To set up the Python environment, run:
```bash
conda create --name ecostress python=3.11
conda activate ecostress
pip install -r requirements.txt
```
:exclamation::exclamation::exclamation: Ensure the `DATA_PATH` in *merge_Tcrits_datasets.py* is set correctly to point to your local data directory. :exclamation::exclamation::exclamation:

---

### **Code Overview**

- **Data Preparation:**  
  **`merge_Tcrits_datasets.py`**: Merges the different Tcrit datasets.

- **Map Generation:**  
  The **`produce_maps`** python scripts generate:  
  - Critical temperature maps  
  - Species count per pixel  
  - Skewness map  
  - TSM maps  
  - Linear regression coefficients per pixel  
  - TSM variations by quantile  

- **Running Experiments:**  
  **`run_experiments.sh`**: Executes all required scripts sequentially.
  In **`produce_maps`**:
  ```bash
  bash run_experiments.sh
  ```

- **Figures and numbers generation:**  
  The **`create_structure_figures_folders.py`** script create the structure of the folders used to save the figures.
  The **`figures_numbers`** scripts create figures and compute numbers for the paper.

---

