# 📘 SEMapp

A GUI to visualize SEM images (using merged .tiff image). 

## 🧪 Description

The GUI can create folders, split merged .tiff files, and rename .tiff files.
Both the merged .tiff and the klarf (.001) files are necessary.

## 📂 Project Structure

# Installation:
## From PyPI (recommanded):

Make sure that Python (> 3.8) is already installed on your computer.

```bash
pip install semapp
```

# Quick start

Launch the application from the Windows search bar:

```
SEMapp
```

Once the GUI opens, select a directory containing klarf (.001) and merged .tiff files.
You must first use the "Create Folder" function. Then, adjust the settings based on the Field of View (FOV).

Merged .tiff files can be split and renamed using the "Split and Rename" function.
The resulting filenames will follow this format:
FOV_Xpos_Ypos_DETECTOR

Where:

FOV: Field of view in µm (e.g., 1, 2, 3, 4…)

DETECTOR: Type of detector used (e.g., BSE, SE1, SE2, etc.)

## How it works 

### Overview 

![How](https://github.com/user-attachments/assets/c1d3bc8b-aebb-4d0c-869d-770910bd123a)

### Settings
![Settings1](https://github.com/user-attachments/assets/9e25459a-5674-4359-8535-b2f6a14e317b)
![Settings2](https://github.com/user-attachments/assets/5491595d-c82c-476d-b2fd-df11617b6d52)
![Settings3](https://github.com/user-attachments/assets/47bb1396-0153-4ce6-8bfc-2bd52ea6dd77)

### Functions

**Create folder**: Allows the creation of subfolders based on file names. The data.tif and klarf (.001) files are moved and renamed. This is important, as it prevents them from being deleted later on.\
**Split .tif and rename** : Allows the main .tif file to be split into individual images. The main file is still retained. Note that the file is split using the tags.\
**Rename (w/o tag)**: If you have the images without captions, you can rename them. The "Defect_i" correspond to the positions "i" found in the main tagged TIFF file. That’s why you need to ask for it with or without tags. **Note that you must first move the klarf file in the subfolder** (e.g., XXXX_RECIPENAME_<span style="color:#FF0000;">NUM_FOLDER</span> must be placed in "w_<span style="color:#FF0000;">NUM_FOLDER</span>" or "<span style="color:#FF0000;">NUM_FOLDER</span>" folder)
**Clean**: Allows you to delete all images except the original .tif file.

# Acknowledgements

Thanks to Joseph for the simplified tutorial !
