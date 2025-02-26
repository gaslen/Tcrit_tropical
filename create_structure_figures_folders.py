import os

base_dir = 'figures'
structure = {
    'Appendix': ['Tcrits', 'TSM_Tcritmax'],
    'Figure1': ['LRmaps', 'TSM2020'],
    'Figure2': ['surface_over_threshold', 'TSM_LR'],
    'Figure3': [],
    'Figure4': []
}

# Create base directory
os.makedirs(base_dir, exist_ok=True)

# Create subdirectories and files
for folder, items in structure.items():
    folder_path = os.path.join(base_dir, folder)
    os.makedirs(folder_path, exist_ok=True)
    for item in items:
        item_path = os.path.join(folder_path, item)
        os.makedirs(item_path, exist_ok=True)

print('Folder structure created successfully!')