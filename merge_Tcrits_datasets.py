import pandas as pd
import numpy as np
from openpyxl import load_workbook

version = "_v21"
DATA_PATH = "/home/nina/Documents/ecostress/data" 


# Create a function to check strikethrough for a specific cell
def is_strikethrough(cell):
    if cell.font and cell.font.strike:
        return True
    return False

if __name__ == "__main__":
    list_sdms_available = pd.read_csv(DATA_PATH + f"/data_species/list_species.csv")["species"].tolist()
    merged_df = pd.DataFrame.from_dict(
        {"Plant species clean": [], "Thermal Tolerance_deg.C": []}
    )

    df_sullivan = pd.read_excel(DATA_PATH + f"/data_species/gcb13477-sup-0002-tables7.xlsx")
    df_sullivan = df_sullivan.rename(
        columns={"Species": "Plant species clean", "Tcrit": "Thermal Tolerance_deg.C"}
    )
    df_sullivan["Plant species clean"] = [
        i.replace(" ", "_").replace("#", "").replace("*", "")
        for i in df_sullivan["Plant species clean"]
    ]
    df_sullivan = df_sullivan[["Plant species clean", "Thermal Tolerance_deg.C"]]
    df_sullivan["Tmin or Tmax"] = "Tmax"
    df_sullivan = df_sullivan[~df_sullivan["Thermal Tolerance_deg.C"].isna()]
    unique_sull = np.unique(df_sullivan["Plant species clean"])
    species_sullivan = set([i for i in df_sullivan["Plant species clean"]])
    nspecies_sullivan = len(species_sullivan)
    common_list2 = species_sullivan.intersection(list_sdms_available)
    print("Sullivan", len(common_list2))
    df_sullivan = df_sullivan[df_sullivan["Plant species clean"].isin(common_list2)]

    # Perez & Feeley: https://onlinelibrary.wiley.com/doi/full/10.1111/jbi.13984
    # Weak phylogenetic and climatic signals in plant heat tolerance
    df_perez = pd.read_csv(DATA_PATH + f"/data_species/Perez.and.Feeley.2020.csv")
    df_perez = df_perez[df_perez["crown.illumination"] >= 4] # remove species with low crown illumination, which can bias Tcrit values
    df_perez = df_perez.rename(
        columns={"species": "Plant species clean", "Tcrit": "Thermal Tolerance_deg.C"}
    )  # T50 instead of Tcrit
    df_perez["Plant species clean"] = [
        i.replace(" ", "_") for i in df_perez["Plant species clean"]
    ]
    df_perez["Tmin or Tmax"] = "Tmax"
    species_perez = set([i for i in df_perez["Plant species clean"]])
    nspecies_perez = len(species_perez)
    common_list = species_perez.intersection(list_sdms_available)
    print("Perez", len(common_list))
    df_perez = df_perez[df_perez["Plant species clean"].isin(common_list)]


    df_slot = pd.read_excel(
        DATA_PATH + f"/data_species/Tcrit_147 tropical_forest_species.xlsx"
    )
    df_slot = df_slot.rename(
        columns={"Species": "Plant species clean", "Tcrit": "Thermal Tolerance_deg.C"}
    )
    df_slot["Tmin or Tmax"] = "Tmax"
    df_slot["Plant species clean"] = [
        i.replace(" ", "_").replace("#", "").replace("*", "")
        for i in df_slot["Plant species clean"]
    ]
    unique_slot = np.unique(df_slot["Plant species clean"])
    species_slot = set([i for i in df_slot["Plant species clean"]])
    nspecies_slot = len(species_slot)
    common_list = species_slot.intersection(list_sdms_available)
    print("Slot", len(common_list))
    df_slot = df_slot[df_slot["Plant species clean"].isin(common_list)]

    # https://nph.onlinelibrary.wiley.com/doi/full/10.1111/nph.19702
    df_bison = pd.read_csv(DATA_PATH + f"/data_species/Bison.csv")
    df_bison = df_bison.rename(
        columns={"name": "Plant species clean", "Tcrit": "Thermal Tolerance_deg.C"}
    )
    unique_bison = np.unique(df_bison["Plant species clean"])
    species_bison = set([i for i in df_bison["Plant species clean"]])
    nspecies_bison = len(species_bison)
    common_list = species_bison.intersection(list_sdms_available)
    print("bison", len(common_list))
    df_bison = df_bison[df_bison["Plant species clean"].isin(common_list)]


    # merged_df = pd.concat([merged_df, df_lancaster])
    merged_df = pd.concat([merged_df, df_sullivan])
    # merged_df = pd.concat([merged_df, df_Middleby])
    # merged_df = pd.concat([merged_df, df_Tarvainen])
    merged_df = pd.concat([merged_df, df_perez])
    # merged_df = pd.concat([merged_df, df_feeley])
    merged_df = pd.concat([merged_df, df_slot])
    merged_df = pd.concat([merged_df, df_bison])
    
    merged_df = merged_df[merged_df["Thermal Tolerance_deg.C"] <= 55]
    merged_df = merged_df[merged_df["Thermal Tolerance_deg.C"] >= 35]


    print("Total", len(set([i for i in merged_df["Plant species clean"]])))
    # print(df_shared.shape, df_slot.shape, df_sullivan.shape, merged_df.shape)

    merged_df.to_csv(
        DATA_PATH + f"/data_species/shared_species{version}.csv", index=False
    )  