# 📘 SEMapp

A GUI to visualize SEM images (using merged .tiff image). 

## 🧪 Description

The GUI create folder, can split merged .tiff images


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

Once the GUI opens, select a directory containing .klarf and merged .tiff files.
You must first use the "Create Folder" function. Then, adjust the settings based on the Field of View (FOV).

Merged .tiff files can be split and renamed using the "Split and Rename" function.
The resulting filenames will follow this format:
FOV_Xpos_Ypos_DETECTOR

Where:

FOV: Field of view in µm (e.g., 1, 2, 3, 4…)

DETECTOR: Type of detector used (e.g., BSE, SE1, SE2, etc.)

## How it works 


![How](https://github.com/user-attachments/assets/c1d3bc8b-aebb-4d0c-869d-770910bd123a)
![How_2](https://github.com/user-attachments/assets/e98e61be-62cd-48f7-b51b-6d5e3e56de17)

# Acknowledgements

Thanks to Joseph for the simplified tutorial !
