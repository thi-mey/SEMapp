"""
A class to manage and display frames in the UI, providing functionality
for plotting and saving combined screenshots of images and plots.
"""
import os
import numpy as np
import glob
import re
import pandas as pd
from PIL import Image
from PyQt5.QtWidgets import QFrame, QGroupBox, QWidget, QVBoxLayout, QPushButton, \
    QGridLayout, QLabel, QFileDialog, QProgressDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from semapp.Plot.utils import create_savebutton
from semapp.Plot.styles import OPEN_BUTTON_STYLE, MESSAGE_BOX_STYLE, FRAME_STYLE

# Constants
FRAME_SIZE = 600
CANVAS_SIZE = 600
radius = 10

class PlotFrame(QWidget):
    """
    A class to manage and display frames in the UI,
    allowing plotting and image viewing.
    Provides functionality to open and display TIFF
    images and plot coordinate mappings.
    """

    def __init__(self, layout, button_frame):
        """
        Initializes the PlotFrame class by setting up the
        UI components and initializing variables.

        :param layout: The layout to which the frames will be added.
        :param button_frame: The button frame containing
        additional control elements.
        """
        super().__init__()
        self.layout = layout
        self.button_frame = button_frame
        
        # Initialize state
        self.coordinates = None
        self.image_list = []
        self.current_index = 0
        self.canvas_connection_id = None
        self.selected_wafer = None
        self.radius = None
        
        self._setup_frames()
        self._setup_plot()
        self._setup_controls()

    def _setup_frames(self):
        """Initialize left and right display frames."""
        # Left frame for images
        self.frame_left = self._create_frame()
        self.frame_left_layout = QVBoxLayout()
        self.frame_left.setLayout(self.frame_left_layout)
        
        # Right frame for plots
        self.frame_right = self._create_frame()
        self.frame_right_layout = QGridLayout()
        self.frame_right.setLayout(self.frame_right_layout)
        
        # Add frames to main layout
        self.layout.addWidget(self.frame_left, 2, 0, 1, 3)
        self.layout.addWidget(self.frame_right, 2, 3, 1, 3)

    def _create_frame(self):
        """Create a styled frame with fixed size."""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet(FRAME_STYLE)
        frame.setFixedSize(FRAME_SIZE+100, FRAME_SIZE)
        return frame

    def _setup_plot(self):
        """Initialize matplotlib figure and canvas."""
        self.figure = Figure(figsize=(5, 5))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.frame_right_layout.addWidget(self.canvas)
        
        # Initialize image display
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.frame_left_layout.addWidget(self.image_label)

    def _setup_controls(self):
        """Set up control buttons."""
        create_savebutton(self.layout, self.frame_left, self.frame_right)
        
        open_button = QPushButton('Open TIFF', self)
        open_button.setStyleSheet(OPEN_BUTTON_STYLE)
        open_button.clicked.connect(self.open_tiff)
        self.layout.addWidget(open_button, 1, 5)
    
    def extract_positions(self, filepath):

        data = {
            "SampleSize": None,
            "DiePitch": {"X": None, "Y": None},
            "DieOrigin": {"X": None, "Y": None},
            "SampleCenterLocation": {"X": None, "Y": None},
            "Defects": []
        }

        dans_defect_list = False

        with open(filepath, "r", encoding="utf-8") as f:
            for ligne in f:
                ligne = ligne.strip()

                if ligne.startswith("SampleSize"):
                    match = re.search(r"SampleSize\s+1\s+(\d+)", ligne)
                    if match:
                        data["SampleSize"] = int(match.group(1))

                elif ligne.startswith("DiePitch"):
                    match = re.search(r"DiePitch\s+([0-9.]+)\s+([0-9.]+);", ligne)
                    if match:
                        data["DiePitch"]["X"] = float(match.group(1))
                        data["DiePitch"]["Y"] = float(match.group(2))

                elif ligne.startswith("DieOrigin"):
                    match = re.search(r"DieOrigin\s+([0-9.]+)\s+([0-9.]+);", ligne)
                    if match:
                        data["DieOrigin"]["X"] = float(match.group(1))
                        data["DieOrigin"]["Y"] = float(match.group(2))

                elif ligne.startswith("SampleCenterLocation"):
                    match = re.search(r"SampleCenterLocation\s+([0-9.]+)\s+([0-9.]+);", ligne)
                    if match:
                        data["SampleCenterLocation"]["X"] = float(match.group(1))
                        data["SampleCenterLocation"]["Y"] = float(match.group(2))

                elif ligne.startswith("DefectList"):
                    dans_defect_list = True
                    continue

                elif dans_defect_list:
                    if re.match(r"^\d+\s", ligne):
                        valeurs = ligne.split()
                        if len(valeurs) >= 18:
                            defect = {f"val{i+1}": float(val) for i, val in enumerate(valeurs[:18])}
                            data["Defects"].append(defect)

        pitch_x = data["DiePitch"]["X"]
        pitch_y = data["DiePitch"]["Y"]
        Xcenter = data["SampleCenterLocation"]["X"]
        Ycenter = data["SampleCenterLocation"]["Y"]

        corrected_positions = []

        for d in data["Defects"]:
            val1 = d["val1"]
            val2 = d["val2"]
            val3 = d["val3"]
            val4_scaled = d["val4"] * pitch_x - Xcenter
            val5_scaled = d["val5"] * pitch_y - Ycenter

            x_corr = round((val2 + val4_scaled) / 10000, 1)
            y_corr = round((val3 + val5_scaled) / 10000, 1)

            corrected_positions.append({
                "defect_id": val1,
                "X": x_corr,
                "Y": y_corr
            })

         
        self.coordinates = pd.DataFrame(corrected_positions, columns=["X", "Y"])

        return self.coordinates

    def load_coordinates(self, csv_path):
        """
        Loads the X/Y coordinates from a CSV file for plotting.

        :param csv_path: Path to the CSV file containing the coordinates.
        """
        if os.path.exists(csv_path):
            self.coordinates = pd.read_csv(csv_path)
            print(f"Coordinates loaded: {self.coordinates.head()}")
        else:
            print(f"CSV file not found: {csv_path}")

    def open_tiff(self):
        """Handle TIFF file opening and display."""
        self.selected_wafer = self.button_frame.get_selected_option()
        
        if not all([self.selected_wafer]):
            print("Recipe and wafer selection required")
            self._reset_display()
            return


        folder_path = os.path.join(self.button_frame.folder_var_changed(), 
                                 str(self.selected_wafer))
        
                # Recherche du fichier qui se termine par .001 dans le dossier
        matching_files = glob.glob(os.path.join(folder_path, '*.001'))

        # Si au moins un fichier correspond, on prend le premier
        if matching_files:
            recipe_path = matching_files[0]
        else:
            recipe_path = None  # Ou tu peux lever une exception ou afficher un message d’erreur
        # Charger les coordonnées depuis le fichier CSV (recipe)
        self.coordinates = self.extract_positions(recipe_path)     
        
        tiff_path = os.path.join(folder_path, "data.tif")

        if not os.path.isfile(tiff_path):
            print(f"TIFF file not found in {folder_path}")
            self._reset_display()
            return

        self._load_tiff(tiff_path)
        self._update_plot()  # Maintenant les coordonnées seront disponibles pour le plot

        # Pop-up stylisé
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Wafer {self.selected_wafer} opened successfully")
        msg.setWindowTitle("Wafer Opened")
        msg.setStyleSheet(MESSAGE_BOX_STYLE)
        msg.exec_()

    def _reset_display(self):
        """
        Resets the display by clearing the figure and reinitializing the subplot.
        Also clears the frame_left_layout to remove any existing widgets.
        """
        # Clear all widgets from the left frame layout
        while self.frame_left_layout.count():
            item = self.frame_left_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # Properly delete the widget

        # Recreate the image label in the left frame
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.frame_left_layout.addWidget(self.image_label)

        # Clear the figure associated with the canvas
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)  # Create a new subplot
        self.plot_mapping_tpl(self.ax)  # Plot the default template

        # Disconnect any existing signal connection
        if self.canvas_connection_id is not None:
            self.canvas.mpl_disconnect(self.canvas_connection_id)
            self.canvas_connection_id = None

        self.canvas.draw()  # Redraw the updated canvas

    def _update_plot(self):
        """
        Updates the plot with the current wafer mapping.
        Ensures the plot is clean before adding new data.
        """
        if hasattr(self, 'ax') and self.ax:
            self.ax.clear()  # Clear the existing plot
        else:
            self.ax = self.figure.add_subplot(111)  # Create new axes

        self.plot_mapping_tpl(self.ax)  # Plot wafer mapping

        # Ensure only one connection to the button press event
        if self.canvas_connection_id is not None:
            self.canvas.mpl_disconnect(self.canvas_connection_id)

        self.canvas_connection_id = self.canvas.mpl_connect(
            'button_press_event', self.on_click)
        self.canvas.draw()

    def show_image(self):
        """
        Displays the current image from the image list in the QLabel.
        """
        if self.image_list:
            pil_image = self.image_list[self.current_index]
            pil_image = pil_image.convert("RGBA")
            data = pil_image.tobytes("raw", "RGBA")
            qimage = QImage(data, pil_image.width, pil_image.height,
                            QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap)

    def plot_mapping_tpl(self, ax):
        """Plots the mapping of the wafer with coordinate points."""
        ax.set_xlabel('X (cm)', fontsize=20)
        ax.set_ylabel('Y (cm)', fontsize=20)
        
        if self.coordinates is not None:
            x_coords = self.coordinates.iloc[:, 0]
            y_coords = self.coordinates.iloc[:, 1]

            # Calcul de la valeur maximale absolue parmi toutes les coordonnées
            max_val = max(abs(x_coords).max(), abs(y_coords).max())

            if max_val <= 5:
                radius = 5
            elif max_val <= 7.5:
                radius = 7.5
            elif max_val <= 10:
                radius = 10
            elif max_val <= 15:
                radius = 15
            else:
                radius = max_val  # fallback pour les cas supérieurs à 30

            self.radius = radius

            ax.scatter(x_coords, y_coords, color='blue', marker='o',
                       s=100, label='Positions')
            
                # Mise à l'échelle du graphique en fonction du radius
            ax.set_xlim(-radius - 1, radius + 1)
            ax.set_ylim(-radius - 1, radius + 1)

            circle = plt.Circle((0, 0), radius, color='black',
                                fill=False, linewidth=0.5)
            ax.add_patch(circle)
            ax.set_aspect('equal')
        else:
            print("No coordinates available to plot")
        

        ax.figure.subplots_adjust(left=0.15, right=0.95, top=0.90, bottom=0.1)
        self.canvas.draw()

    def on_click(self, event):
        """
        Handles mouse click events on the plot, identifying the closest point
        and updating the plot with a red circle around the selected point.

        :param event: The event generated by the mouse click.
        """
        result = self.button_frame.get_selected_image()
        if result is not None:
            self.image_type, self_number_type = result
        else:
            print("No image selected.")
            return

        if event.inaxes:
            x_pos = event.xdata
            y_pos = event.ydata


            if self.coordinates is not None and not self.coordinates.empty:
                distances = np.sqrt((self.coordinates['X'] - x_pos) ** 2 +
                                    (self.coordinates['Y'] - y_pos) ** 2)
                closest_idx = distances.idxmin()
                closest_pt = self.coordinates.iloc[closest_idx]
                print(f"The closest point is: X = {closest_pt['X']}, "
                      f"Y = {closest_pt['Y']}")

                # Replot with a red circle around the selected point
                self.ax.clear()  # Clear the existing plot
                self.plot_mapping_tpl(self.ax)
                self.ax.scatter([closest_pt['X']], [closest_pt['Y']],
                                color='red', marker='o', s=100,
                                label='Selected point')
                coord_text = f"{closest_pt['X']:.1f} / {closest_pt['Y']:.1f}"
                self.ax.text(-self.radius -0.5, self.radius-0.5, coord_text, fontsize=16, color='black')
                self.canvas.draw()

                # Update the image based on the selected point
                result = self.image_type + (closest_idx * self_number_type)
                self.current_index = result
                self.show_image()

    def _load_tiff(self, tiff_path):
        """Load and prepare TIFF images for display.
        
        Args:
            tiff_path: Path to the TIFF file to load
        """
        try:
            img = Image.open(tiff_path)
            self.image_list = []

            # Load all TIFF pages and resize them
            while True:
                resized_img = img.copy().resize((CANVAS_SIZE, CANVAS_SIZE),
                                              Image.Resampling.LANCZOS)
                self.image_list.append(resized_img)
                try:
                    img.seek(img.tell() + 1)  # Move to next page
                except EOFError:
                    break  # No more pages

            self.current_index = 0
            self.show_image()  # Display first image
            
        except Exception as e:
            print(f"Error loading TIFF file: {e}")
            self._reset_display()
