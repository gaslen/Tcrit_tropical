import pandas as pd
import numpy as np
from openpyxl import load_workbook

version = "_v15"
DATA_PATH = "/home/nina/Documents/ecostress/data" #"/data/gaston/ecostress"

# T50: some of Lancaster and Feeley. Slot and Perez can also be used with T50.


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

    df_lancaster = pd.read_excel(DATA_PATH + f"/data_species/pnas.1918162117.sd01.xlsx")
    df_lancaster = df_lancaster[df_lancaster["Tmin or Tmax"] == "Tmax"]
    df_lancaster["Tolerance measure"][
        (df_lancaster["Tolerance measure"] == "T50")
    ] = "Tcrit"
    df_lancaster = df_lancaster[
        (df_lancaster["Tolerance measure"] == "Tcrit")
    ]  
    species = set([i for i in df_lancaster["Plant species clean"]])
    list_nature = df_lancaster["Plant species clean"].tolist()
    common_list = set(list_nature).intersection(list_sdms_available)
    print("Lancaster", len(common_list))
    df_lancaster = df_lancaster[df_lancaster["Plant species clean"].isin(common_list)]

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

    df_Middleby = pd.DataFrame.from_dict(
        {
            "Plant species clean": [
                "Terminalia_microcarpa",
                "Castanospermum_australe",
                "Castanospermum_australe",
            ],
            "Thermal Tolerance_deg.C": [47.7, 46.6, 49.6],
        }
    )
    df_Middleby["Tmin or Tmax"] = "Tmax"
    species_Middleby = set([i for i in df_Middleby["Plant species clean"]])
    common_list = species_Middleby.intersection(list_sdms_available)
    print("Middleby", len(common_list))
    df_Middleby = df_Middleby[df_Middleby["Plant species clean"].isin(common_list)]
    # from: https://www.authorea.com/users/802804/articles/1187938-ecotypic-variation-in-leaf-thermoregulation-and-heat-tolerance-but-not-thermal-safety-margins-in-tropical-trees


    df_Tarvainen = pd.DataFrame.from_dict(
        {
            "Plant species clean": [
                "Harungana_montana",
                "Syzygium_guineense",
                "Entandrophragma_exselsum",
            ],
            "Thermal Tolerance_deg.C": [40, 40, 40],
        }
    )
    df_Tarvainen["Tmin or Tmax"] = "Tmax"  # 3 especes anyway...
    species_Tarvainen = set([i for i in df_Tarvainen["Plant species clean"]])
    common_list = species_Tarvainen.intersection(list_sdms_available)
    print("Tarvainen", len(common_list))
    df_Tarvainen = df_Tarvainen[df_Tarvainen["Plant species clean"].isin(common_list)]


    # Perez & Feeley: https://onlinelibrary.wiley.com/doi/full/10.1111/jbi.13984
    # Weak phylogenetic and climatic signals in plant heat tolerance
    df_perez = pd.read_csv(DATA_PATH + f"/data_species/Perez.and.Feeley.2020.csv")
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


    file_path = DATA_PATH + f"/data_species/Table_1_Feeley.xlsx"
    # https://www.frontiersin.org/journals/forests-and-global-change/articles/10.3389/ffgc.2020.00025/full#h11
    df_feeley = pd.read_excel(file_path, skiprows=2)
    # Load the workbook with openpyxl
    wb = load_workbook(file_path)
    sheet = wb.active  # Get the active sheet (or use sheet names)
    for row in sheet.iter_rows(
        min_row=4, max_row=sheet.max_row, min_col=1, max_col=sheet.max_column
    ):
        for cell in row:
            if is_strikethrough(cell):
                df_feeley.iloc[cell.row - 4, cell.column - 1] = f"Strikethrough"
    df_feeley = df_feeley[df_feeley["T50 (95% CI)"] != "Strikethrough"]
    df_feeley = df_feeley[~df_feeley["Species"].isnull()]
    df_feeley["T50 (95% CI)"] = [float(i.split(" ")[0]) for i in df_feeley["T50 (95% CI)"]]
    df_feeley = df_feeley.rename(
        columns={
            "Species": "Plant species clean",
            "T50 (95% CI)": "Thermal Tolerance_deg.C",
        }
    )
    df_feeley["Plant species clean"] = [
        i.replace(" ", "_") for i in df_feeley["Plant species clean"]
    ]
    df_feeley["Tmin or Tmax"] = "Tmax"
    species_feeley = set([i for i in df_feeley["Plant species clean"]])
    common_list = species_feeley.intersection(list_sdms_available)
    print("Feeley", len(common_list))
    df_feeley = df_feeley[df_feeley["Plant species clean"].isin(common_list)]

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


    print("Total", len(set([i for i in merged_df["Plant species clean"]])))
    # print(df_shared.shape, df_slot.shape, df_sullivan.shape, merged_df.shape)

    merged_df.to_csv(
        DATA_PATH + f"/data_species/shared_species{version}.csv", index=False
    )  # v6: add sullivan, keep only T50 and Tcrit
    # v7: remove sullivan and Lancaster T50. Only Tcrit from Lancaster and Slot.
    # v8: Re-add Sullivan and lancaster T50
    # v9: add feeley and perez. Add middleby et Tarvainen
    # v10: Remove lancaster et sullivan pour garder les méthodes consistantes entre elles.
    # v11: remove outlier small value
    # v12: reput outliers and sullivan.
    # v13: remove df_Tarvainen and df_feeley because it was actually t50. Re-add sullivan
    # v14: remove species above 55 deg.
    # v15: add bison
    # v16: only slot and perez for comparable methods
    # v17: only sullivan and bison
