# This file adds numbering to the beginning of files (regardless of extension).
# Doing this on images and texts makes it easier to keep track which ones have been
# processed.
import os

def rename_files_with_offset(folder_path, offset=0):
    files = sorted(os.listdir(folder_path))
    for i, filename in enumerate(files):
        old_path = os.path.join(folder_path, filename)
        if os.path.isfile(old_path):
            new_filename = f"{i + offset}_{filename}"
            new_path = os.path.join(folder_path, new_filename)
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_filename}")


folder_to_rename = 'data_100(bottom)_images'
starting_offset = 100
rename_files_with_offset(folder_to_rename, starting_offset)
