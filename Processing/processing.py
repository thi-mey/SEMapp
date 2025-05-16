"""
Module for processing and renaming TIFF files based on CSV coordinates.
"""

import json
import re
import glob
import shutil
import os
from PIL import Image
import pandas as pd


class Process:
    """
    A class to handle processing of TIFF files and renaming them based on
    coordinates from a CSV file.
    """

    def __init__(self, dirname, wafer=None, scale=None):
        """
        Initialize the processing instance with necessary parameters.

        Args:
            dirname (str): The base directory for the files.
            recipe (str): The CSV file containing coordinates.
            wafer (str): The wafer number (optional).
            scale (str): The path to the settings JSON file (optional).
        """
        self.dirname = dirname
        self.scale_data = scale
        self.wafer_number = str(wafer)
        self.tiff_path = None
        self.coordinates = None
        self.settings = None
        self.output_dir = None
        self.load_json()
    def load_json(self):
        """Load the settings data from a JSON file."""
        try:
            with open(self.scale_data, "r", encoding="utf-8") as file:
                self.settings = json.load(file)
            print("Settings data loaded successfully.")
        except FileNotFoundError:
            print("Settings file not found. Starting fresh.")
            self.settings = []
        except json.JSONDecodeError as error:
            print(f"JSON decoding error: {error}")
            self.settings = []
        except OSError as error:
            print(f"OS error when reading file: {error}")
            self.settings = []   
    def extract_positions(self, filepath):
        '''Function to extract positions from a 001 file.'''
        data = {
            "SampleSize": None,
            "DiePitch": {"X": None, "Y": None},
            "DieOrigin": {"X": None, "Y": None},
            "SampleCenterLocation": {"X": None, "Y": None},
            "Defects": []
        }

        dans_defect_list = False

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if line.startswith("SampleSize"):
                    match = re.search(r"SampleSize\s+1\s+(\d+)", line)
                    if match:
                        data["SampleSize"] = int(match.group(1))

                elif line.startswith("DiePitch"):
                    match = re.search(r"DiePitch\s+([0-9.]+)\s+([0-9.]+);", line)
                    if match:
                        data["DiePitch"]["X"] = float(match.group(1))
                        data["DiePitch"]["Y"] = float(match.group(2))

                elif line.startswith("DieOrigin"):
                    match = re.search(r"DieOrigin\s+([0-9.]+)\s+([0-9.]+);", line)
                    if match:
                        data["DieOrigin"]["X"] = float(match.group(1))
                        data["DieOrigin"]["Y"] = float(match.group(2))

                elif line.startswith("SampleCenterLocation"):
                    match = re.search(r"SampleCenterLocation\s+([0-9.]+)\s+([0-9.]+);", line)
                    if match:
                        data["SampleCenterLocation"]["X"] = float(match.group(1))
                        data["SampleCenterLocation"]["Y"] = float(match.group(2))

                elif line.startswith("DefectList"):
                    dans_defect_list = True
                    continue

                elif dans_defect_list:
                    if re.match(r"^\d+\s", line):
                        value = line.split()
                        if len(value) >= 18:
                            defect = {f"val{i+1}": float(val) for i, val in enumerate(value[:18])}
                            data["Defects"].append(defect)

        pitch_x = data["DiePitch"]["X"]
        pitch_y = data["DiePitch"]["Y"]
        x_center = data["SampleCenterLocation"]["X"]
        y_center = data["SampleCenterLocation"]["Y"]

        corrected_positions = []

        for d in data["Defects"]:
            val1 = d["val1"]
            val2 = d["val2"]
            val3 = d["val3"]
            val4_scaled = d["val4"] * pitch_x - x_center
            val5_scaled = d["val5"] * pitch_y - y_center

            x_corr = round((val2 + val4_scaled) / 10000, 1)
            y_corr = round((val3 + val5_scaled) / 10000, 1)

            corrected_positions.append({"defect_id": val1, "X": x_corr,"Y": y_corr})

        self.coordinates = pd.DataFrame(corrected_positions, columns=["X", "Y"])

        return self.coordinates
    def rename(self):
        """
        Rename TIFF files based on the coordinates from the CSV file.

        This method processes TIFF files in the wafer directory and renames
        them using the corresponding X/Y coordinates and settings values.
        """
        self.output_dir = os.path.join(self.dirname, self.wafer_number)

        if not os.path.exists(self.output_dir):
            print(f"Directory not found: {self.output_dir}")
            return

        matching_files = glob.glob(os.path.join(self.output_dir, '*.001'))

        # If at least one file matches, take the first one
        if matching_files:
            recipe_path = matching_files[0]
        else:
            recipe_path = None  
        self.coordinates = self.extract_positions(recipe_path)



        tiff_files = [f for f in os.listdir(self.output_dir)
                      if "page" in f and f.lower().endswith(('.tiff', '.tif'))]
        tiff_files.sort()

        for file in tiff_files:
            # Extract page number from the file name (e.g., data_page_1.tiff)
            file_number = int(file.split('_')[2].split('.')[0])
            print(f"Processing {file}: Page number {file_number}, Total "
                  f"settings {len(self.settings)}")

            # Calculate the corresponding row in the CSV
            csv_row_index = (file_number - 1) // len(self.settings)
            remainder = (file_number - 1) % len(self.settings)

            # Get X/Y coordinates from the CSV
            x = self.coordinates.iloc[csv_row_index, 0]  # First column for X
            y = self.coordinates.iloc[csv_row_index, 1]  # Second column for Y

            # Get settings values (Scale, Image Type)
            scale = self.settings[remainder]["Scale"]
            image_type = self.settings[remainder]["Image Type"]

            # Construct the new file name
            new_name = f"{scale}_{x}_{y}_{image_type}.tif"

            old_path = os.path.join(self.output_dir, file)
            new_path = os.path.join(self.output_dir, new_name)

            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed: {file} -> {new_name}")
            
    def split_tiff(self):
        """
        Split a merged TIFF file into individual TIFF files.

        Returns:
            list: List of file paths of the generated TIFF files.
        """
        self.tiff_path = os.path.join(self.dirname,
                                      self.wafer_number,
                                      "data.tif")
        

        output_files = []
        page_index = 0
        if not os.path.exists(self.tiff_path):
            print(f"TIFF file not found: {self.tiff_path}")
            return []

        try:
            img = Image.open(self.tiff_path)
            while True:
                output_file = self.tiff_path.replace(".tif", "") + \
                              f"_page_{page_index + 1}.tiff"
                img.save(output_file, format="TIFF")
                output_files.append(output_file)

                try:
                    img.seek(page_index + 1)
                    page_index += 1
                except EOFError:
                    break
        except Exception as error:
            raise RuntimeError(f"Error splitting TIFF file: {error}") from error

        return output_files
    
    def clean(self):
        """
        Clean up the output directory by deleting any non-conforming TIFF files.

        This method deletes any files that do not follow the expected naming
        conventions (files not starting with "data" or
        containing the word "page").
        """
        self.output_dir = os.path.join(self.dirname, self.wafer_number)

        if not os.path.exists(self.output_dir):
            print(f"Error: Directory does not exist: {self.output_dir}")
            return

        tiff_files = [f for f in os.listdir(self.output_dir)
                      if f.lower().endswith(('.tiff', '.tif'))]

        # Delete non-conforming files
        for file_name in tiff_files:
            if not file_name.startswith("data") or "page" in file_name.lower() or file_name.endswith("001"):
                file_path = os.path.join(self.output_dir, file_name)
                os.remove(file_path)
                print(f"Deleted: {file_path}")

    def split_tiff_all(self):
        """
        Split all merged TIFF files in the directory (including subdirectories)
        into individual TIFF files.

        This method will look through all directories and split each `data.tif`
        file into separate pages.
        """
        for subdir, _, _ in os.walk(self.dirname):
            if subdir != self.dirname:
                self.tiff_path = os.path.join(subdir, "data.tif")
                print(f"Processing directory: {subdir}, "
                      f"TIFF path: {self.tiff_path}")

                output_files = []
                page_index = 0
                if not os.path.exists(self.tiff_path):
                    print(f"TIFF file not found: {self.tiff_path}")
                    continue

                try:
                    img = Image.open(self.tiff_path)
                    while True:
                        output_file = self.tiff_path.replace(".tif", "") + \
                                      f"_page_{page_index + 1}.tiff"
                        img.save(output_file, format="TIFF")
                        output_files.append(output_file)

                        try:
                            img.seek(page_index + 1)
                            page_index += 1
                        except EOFError:
                            break
                except Exception as error:
                    raise RuntimeError(f"Error splitting "
                                       f"TIFF file: {error}") from error

    def rename_all(self):
        """
        Rename all TIFF files based on the coordinates from the
        CSV file in all subdirectories.

        This method will iterate through all subdirectories,
        loading the CSV and settings, and renaming files accordingly.
        """

        for subdir, _, _ in os.walk(self.dirname):
            if subdir != self.dirname:
                self.output_dir = os.path.join(self.dirname,
                                               os.path.basename(subdir))
                print(f"Renaming files in: {self.output_dir}")

                matching_files = glob.glob(os.path.join(self.output_dir, '*.001'))

                if matching_files:
                    recipe_path = matching_files[0]
                else:
                    return
                self.coordinates = self.extract_positions(recipe_path)

                if self.coordinates is None or self.coordinates.empty:
                    raise ValueError("Coordinates have not been loaded or are empty.")

                tiff_files = [f for f in os.listdir(self.output_dir)
                              if "page" in f and
                              f.lower().endswith(('.tiff', '.tif'))]
                tiff_files.sort()

                for file in tiff_files:
                    file_number = int(file.split('_')[2].split('.')[0])
                    print(f"Processing {file}: Page number {file_number}, "
                          f"Total settings {len(self.settings)}")

                    csv_row_index = (file_number - 1) // len(self.settings)
                    remainder = (file_number - 1) % len(self.settings)

                    x = self.coordinates.iloc[csv_row_index, 0]
                    y = self.coordinates.iloc[csv_row_index, 1]

                    scale = self.settings[remainder]["Scale"]
                    image_type = self.settings[remainder]["Image Type"]

                    new_name = f"{scale}_{x}_{y}_{image_type}.tif"
                    old_path = os.path.join(self.output_dir, file)
                    new_path = os.path.join(self.output_dir, new_name)

                    os.rename(old_path, new_path)
                    print(f"Renamed: {file} -> {new_name}")

    def clean_all(self):
        """
        Delete all non-conforming TIFF files in all subdirectories.

        This method will remove any files that do not follow the expected
         naming conventions in all directories.
        """
        for subdir, _, _ in os.walk(self.dirname):
            if subdir != self.dirname:
                self.output_dir = os.path.join(self.dirname,
                                               os.path.basename(subdir))
                print(f"Cleaning directory: {self.output_dir}")

                if not os.path.exists(self.output_dir):
                    print(f"Error: Directory does not exist: {self.output_dir}")
                    continue

                tiff_files = [f for f in os.listdir(self.output_dir)
                              if f.lower().endswith(('.tiff', '.tif'))]
                for file_name in tiff_files:
                    if not file_name.startswith("data") or \
                            "page" in file_name.lower() or file_name.endswith("001"):
                        file_path = os.path.join(self.output_dir, file_name)
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")

    def organize_and_rename_files(self):
        """
        Organize TIFF files into subfolders based
        on the last split of their name
        and rename the files to 'data.tif' in their respective subfolders.
        """
        if not os.path.exists(self.dirname):
            print(f"Error: The folder {self.dirname} does not exist.")
            return

        # Iterate through files in the directory
        for file_name in os.listdir(self.dirname):
            if file_name.lower().endswith(".tif"):
                parts = file_name.rsplit("_", 1)
                if len(parts) < 2:
                    print(
                        f"Skipping file with unexpected format: {file_name}")
                    continue

                # Use the last part (before extension) as the subfolder name
                subfolder_name = parts[-1].split(".")[0]
                subfolder_path = os.path.join(self.dirname, subfolder_name)

                # Create the subfolder if it does not exist
                os.makedirs(subfolder_path, exist_ok=True)

                # Move and rename the file
                source_path = os.path.join(self.dirname, file_name)
                destination_path = os.path.join(subfolder_path, "data.tif")
                shutil.move(source_path, destination_path)

                print(
                    f"Moved and renamed: {file_name} -> {destination_path}")
            
            if file_name.lower().endswith(".001"):
                parts = file_name.rsplit("_", 1)
                if len(parts) < 2:
                    print(
                        f"Skipping file with unexpected format: {file_name}")
                    continue

                # Use the last part (before extension) as the subfolder name
                subfolder_name = parts[-1].split(".")[0]
                subfolder_path = os.path.join(self.dirname, subfolder_name)

                # Create the subfolder if it does not exist
                os.makedirs(subfolder_path, exist_ok=True)

                # Move and rename the file
                source_path = os.path.join(self.dirname, file_name)
                destination_path = os.path.join(subfolder_path, file_name)
                shutil.move(source_path, destination_path)

                print(
                    f"Moved and renamed: {file_name} -> {destination_path}")

    def rename_wo_legend_all(self):
        """
        Preprocess all files by renaming them based on coordinates from the CSV.
        This method works on folders containing 'Topography1.tiff'.
        """
        folder_names = []

        # Find all subfolders containing "Topography1.tiff"
        for subdir, _, files in os.walk(self.dirname):
            for file in files:
                if file.endswith(".001"):
                    folder_names.append(subdir)

        print(folder_names)  # debug print

        # Process each folder found
        for folder in folder_names:
            for subdir, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(".tiff"):
                        print(subdir)
                        print(f"Processing: {file}")
                        old_filepath = os.path.join(subdir, file)

                        matching_files = glob.glob(os.path.join(folder, '*.001'))
                        print("Found .001 files:", matching_files)  # debug print

                        if matching_files:
                            recipe_path = matching_files[0]
                            self.coordinates = self.extract_positions(recipe_path)
                        else:
                            return
                        

                        print(self.coordinates)

                        try:
                            defect_part = int(file.split("_")[1]) - 1
                            print(f"Defect part index: {defect_part}")
                        except (IndexError, ValueError):
                            print(
                                f"Skipping file due to unexpected format: {file}")
                            continue

                        # Check if defect part is within the valid range


                        # Get X and Y coordinates
                    

                        if defect_part >= len(self.coordinates):
                            print(
                                f"Skipping file {file} due to out-of-bounds "
                                f"defect part.")
                            continue

                        x = self.coordinates.iloc[defect_part, 0]
                        y = self.coordinates.iloc[defect_part, 1]
                        new_filename = f"{x}_{y}"

                        # Add specific suffix based on the file type
                        if "_Class_1_Internal" in file:
                            new_filename += "_BSE.tif"
                        elif "_Class_1_Topography" in file:
                            topo_number = file.split("_Class_1_Topography")[1][
                                0]  # Extract Topography number
                            new_filename += f"_SE{topo_number}.tiff"
                        else:
                            print(
                                f"Skipping file due to unexpected format: {file}")
                            continue

                        # Construct the new file path and rename
                        new_filepath = os.path.join(subdir, new_filename)
                        os.rename(old_filepath, new_filepath)
                        print(f"Renamed: {old_filepath} -> {new_filepath}")

    def rename_wo_legend(self):
        """
        Preprocess TIFF files for a specific wafer
        by renaming based on coordinates.
        This method processes the folder for the specified wafer.
        """
        wafer_path = os.path.join(self.dirname, self.wafer_number)
        if not os.path.exists(wafer_path):
            print(f"Error: The wafer folder {wafer_path} does not exist.")
            return

        for subdir, _, files in os.walk(wafer_path):
            for file in files:
                if file.endswith(".tiff"):
                    print(f"Processing: {file}")

                    old_filepath = os.path.join(subdir, file)

                    try:
                        defect_part = int(file.split("_")[1]) - 1
                        print(f"Defect part index: {defect_part}")
                    except (IndexError, ValueError):
                        print(
                            f"Skipping file due to unexpected format: {file}")
                        continue
                    
                    matching_files = glob.glob(os.path.join(wafer_path, '*.001'))

                    print("Found .001 files:", matching_files)  # debug print

                    if matching_files:
                        recipe_path = matching_files[0]
                    else:
                        return
                    self.coordinates = self.extract_positions(recipe_path)
                    
                    # Check if defect part is within the valid range
                    if defect_part >= len(self.coordinates):
                        print(
                            f"Skipping file {file} "
                            f"due to out-of-bounds defect part.")
                        continue

                    x = self.coordinates.iloc[defect_part, 0]
                    y = self.coordinates.iloc[defect_part, 1]
                    new_filename = f"{x}_{y}"

                    # Add specific suffix based on the file type
                    if "_Class_1_Internal" in file:
                        new_filename += "_BSE.tiff"
                    elif "_Class_1_Topography" in file:
                        topo_number = file.split("_Class_1_Topography")[1][
                            0]  # Extract Topography number
                        new_filename += f"_SE{topo_number}.tiff"
                    else:
                        print(
                            f"Skipping file due to unexpected format: {file}")
                        continue

                    # Construct the new file path and rename
                    new_filepath = os.path.join(subdir, new_filename)
                    os.rename(old_filepath, new_filepath)
                    print(f"Renamed: {old_filepath} -> {new_filepath}")

    def clean_folders_and_files(self):
        """
        Clean up folders and files by deleting specific TIFF files
        """
        for folder, subfolders, files in os.walk(self.dirname):           
            # Rename folders like "w01" -> "1"
            for subfolder in subfolders:
                match = re.fullmatch(r"w0*(\d+)", subfolder)
                if match:
                    new_name = match.group(1)
                    old_path = os.path.join(folder, subfolder)
                    new_path = os.path.join(folder, new_name)

                    # Avoid name conflicts
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        print(f"Renamed: {old_path} -> {new_path}")
                    else:
                        print(f"Conflict: {new_path} already exists. Skipped renaming.")
    
        for folder, subfolders, files in os.walk(self.dirname):
            # Delete .tiff files that contain "Raw" in their name
            for file in files:
                if file.endswith(".tiff") and "Raw" in file:
                    print(file)
                    file_path = os.path.join(folder, file)
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")

if __name__ == "__main__":
    DIRNAME = r"C:\Users\TM273821\Desktop\SEM\RAW"
    SCALE = r"C:\Users\TM273821\SEM\settings_data.json"

    processor = Process(DIRNAME, wafer=18, scale=SCALE)

    # Process files
    # processor.organize_and_rename_files()  # Organize and rename files
    # processor.rename_wo_legend_all()  # Preprocess all files in the directory
    # processor.clean_folders_and_files()
    processor.rename_wo_legend()  # Preprocess specific wafer

    # processor.split_tiff_all()  # Preprocess specific wafer
    # processor.split_tiff_all()  # Preprocess specific wafer
    # processor.split_tiff()  # Preprocess specific wafer
    # processor.rename_all()  # Preprocess specific wafer
    

