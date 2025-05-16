"""Module for buttons"""
# pylint: disable=no-name-in-module, trailing-whitespace, too-many-branches, too-many-statements


import sys
import os
import time
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtWidgets import (
    QWidget, QButtonGroup, QPushButton, QLabel, QGroupBox, QGridLayout,
    QFileDialog, QProgressDialog, QRadioButton, QSizePolicy)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt 
from semapp.Processing.processing import Process
from semapp.Layout.styles import (
    RADIO_BUTTON_STYLE,
    SETTINGS_BUTTON_STYLE,
    RUN_BUTTON_STYLE,
    GROUP_BOX_STYLE,
    WAFER_BUTTON_DEFAULT_STYLE,
    WAFER_BUTTON_EXISTING_STYLE,
    WAFER_BUTTON_MISSING_STYLE,
    SELECT_BUTTON_STYLE,
    PATH_LABEL_STYLE,
)
from semapp.Layout.settings import SettingsWindow

class ButtonFrame(QWidget):
    """Class to create the various buttons of the interface"""

    def __init__(self, layout):
        super().__init__()
        self.layout = layout
        self.folder_path = None
        self.check_vars = {}
        self.common_class = None
        self.folder_path_label = None
        self.radio_vars = {} 
        self.selected_option = None
        self.selected_image = None
        self.table_data = None
        self.table_vars = None

        self.rename = QRadioButton("Rename")
        self.split_rename = QRadioButton("Split .tif and rename (w/ tag)")
        self.split_rename_all = QRadioButton("Split .tif and rename (w/ tag)")
        self.clean = QRadioButton("Clean")
        self.rename = QRadioButton("Rename (w/o tag)")
        self.rename_all = QRadioButton("Rename (w/o tag)")
        self.clean_all = QRadioButton("Clean")
        self.create_folder = QRadioButton("Create folders")

        self.line_edits = {}

        tool_radiobuttons = [self.rename, self.split_rename,
                             self.clean, self.rename_all,
                             self.split_rename_all, self.clean_all,
                             self.create_folder]

        for radiobutton in tool_radiobuttons:
            radiobutton.setStyleSheet(RADIO_BUTTON_STYLE)

        # Example of adding them to a layout
        self.entries = {}
        self.dirname = None
        # self.dirname = r"C:\Users\TM273821\Desktop\SEM\Amel"


        max_characters = 30  # Set character limit
        if self.dirname:
            self.display_text = self.dirname if len(
                self.dirname) <= max_characters else self.dirname[
                                                     :max_characters] + '...'

        # Get the user's folder path (C:\Users\XXXXX)
        self.user_folder = os.path.expanduser(
            "~")  # This gets C:\Users\XXXXX

        # Define the new folder you want to create
        self.new_folder = os.path.join(self.user_folder, "SEM")


        # Create the folder if it doesn't exist
        self.create_directory(self.new_folder)

        self.button_group = QButtonGroup(self)

        self.init_ui()

    def create_directory(self, path):
        """Create the directory if it does not exist."""
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directory created: {path}")
        else:
            print(f"Directory already exists: {path}")

    def init_ui(self):
        """Initialize the user interface"""
        # Add widgets to the grid layout provided by the main window

        self.settings_window = SettingsWindow()
        self.dir_box()
        self.create_wafer()
        self.create_radiobuttons_other()
        self.create_radiobuttons()
        self.create_radiobuttons_all()
        self.image_radiobuttons()
        self.add_settings_button()
        self.create_run_button()
        self.update_wafer()
        self.settings_window.data_updated.connect(self.refresh_radiobuttons)


    def add_settings_button(self):
        """Add a Settings button that opens a new dialog"""
        settings_button = QPushButton("Settings")
        settings_button.setStyleSheet(SETTINGS_BUTTON_STYLE)
        settings_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        settings_button.clicked.connect(self.open_settings_window)

        self.layout.addWidget(settings_button, 0, 4, 1, 1)

    def open_settings_window(self):
        """Open the settings window"""

        self.settings_window.exec_()

    def dir_box(self):
        """Create a smaller directory selection box"""

        # Create layout for this frame
        frame_dir = QGroupBox("Directory")

        frame_dir.setStyleSheet(GROUP_BOX_STYLE)

        # Button for selecting folder
        select_folder_button = QPushButton("Select Parent Folder...")
        select_folder_button.setStyleSheet(SELECT_BUTTON_STYLE)

        # Create layout for the frame and reduce its margins
        frame_dir_layout = QGridLayout()
        frame_dir_layout.setContentsMargins(5, 20, 5, 5)  # Reduced margins
        frame_dir.setLayout(frame_dir_layout)

        # label for folder path
        if self.dirname:
            self.folder_path_label = QLabel(self.display_text)
        else:
            self.folder_path_label = QLabel()

        self.folder_path_label.setStyleSheet(PATH_LABEL_STYLE)

        # Connect the button to folder selection method
        select_folder_button.clicked.connect(self.on_select_folder_and_update)

        # Add widgets to layout
        frame_dir_layout.addWidget(select_folder_button, 0, 0, 1, 1)
        frame_dir_layout.addWidget(self.folder_path_label, 1, 0, 1, 1)

        # Add frame to the main layout with a smaller footprint
        self.layout.addWidget(frame_dir, 0, 0)

    def folder_var_changed(self):
        """Update parent folder"""
        return self.dirname

    def on_select_folder_and_update(self):
        """Method to select folder and update checkbuttons"""
        self.select_folder()
        self.update_wafer()

    def update_wafer(self):
        """Update the appearance of radio buttons based on the existing
        subdirectories in the specified directory."""
        if self.dirname:
            # List the subdirectories in the specified directory
            subdirs = [d for d in os.listdir(self.dirname) if
                       os.path.isdir(os.path.join(self.dirname, d))]

            # Update the style of radio buttons based on the subdirectory presence
            for number in range(1, 27):
                radio_button = self.radio_vars.get(number)
                if radio_button:
                    if str(number) in subdirs:
                        radio_button.setStyleSheet(WAFER_BUTTON_EXISTING_STYLE)
                    else:
                        radio_button.setStyleSheet(WAFER_BUTTON_MISSING_STYLE)
        else:
            # Default style for all radio buttons if no directory is specified
            for number in range(1, 27):
                radio_button = self.radio_vars.get(number)
                radio_button.setStyleSheet(WAFER_BUTTON_MISSING_STYLE)

    def create_wafer(self):
        """Create a grid of radio buttons for wafer slots with exclusive selection."""
        group_box = QGroupBox("Wafer Slots")  # Add a title to the group
        group_box.setStyleSheet(GROUP_BOX_STYLE)  

        wafer_layout = QGridLayout()
        wafer_layout.setContentsMargins(2, 20, 2, 2)  # Reduce internal margins
        wafer_layout.setSpacing(5)  # Reduce spacing between widgets

        

        # Add radio buttons from 1 to 24, with 12 buttons per row
        for number in range(1, 27):
            radio_button = QRadioButton(str(number))
            radio_button.setStyleSheet(WAFER_BUTTON_DEFAULT_STYLE)

            # Connect the radio button to a handler for exclusive selection
            radio_button.toggled.connect(self.get_selected_option)
            self.radio_vars[number] = radio_button

            # Calculate the row and column for each radio button in the layout
            row = (number - 1) // 13  # Row starts at 0
            col = (number - 1) % 13  # Column ranges from 0 to 12

            wafer_layout.addWidget(radio_button, row, col)

        group_box.setLayout(wafer_layout)

        # Add the QGroupBox to the main layout
        self.layout.addWidget(group_box, 1, 0, 1, 4)

    def get_selected_option(self):
        """Ensure only one radio button is selected at a time and track the selected button."""
        selected_number = None  # Variable to store the selected radio button number

        # Iterate over all radio buttons
        for number, radio_button in self.radio_vars.items():
            if radio_button.isChecked():
                selected_number = number  # Track the currently selected radio button

        if selected_number is not None:
            self.selected_option = selected_number  # Store the selected option for further use
            return self.selected_option

    def image_radiobuttons(self):
        """Create a grid of radio buttons for wafer slots with exclusive selection."""
        self.table_data = self.settings_window.get_table_data()
        print(self.table_data)
        number = len(self.table_data)

        group_box = QGroupBox("Image type")  # Add a title to the group
        group_box.setStyleSheet(GROUP_BOX_STYLE)  # Style the title

        wafer_layout = QGridLayout()
        wafer_layout.setContentsMargins(2, 20, 2, 2)  # Reduce internal margins
        wafer_layout.setSpacing(5)  # Reduce spacing between widgets

        self.table_vars = {}  # Store references to radio buttons

        # Add radio buttons from 1 to 24, with 12 radio buttons per row
        for i in range(number):
            label = str(self.table_data[i]["Scale"]) + " - " + str(
                self.table_data[i]["Image Type"])
            radio_button = QRadioButton(label)
            radio_button.setStyleSheet(WAFER_BUTTON_DEFAULT_STYLE)

            # Connect the radio button to a handler for exclusive selection
            radio_button.toggled.connect(self.get_selected_image)
            self.table_vars[i] = radio_button

            # Calculate the row and column for each radio button in the layout
            row = (i) // 3  # Row starts at 1 after the label
            col = (i) % 3  # Column ranges from 0 to 11

            wafer_layout.addWidget(radio_button, row, col)

        group_box.setLayout(wafer_layout)

        # Add the QGroupBox to the main layout
        self.layout.addWidget(group_box, 1, 4, 1, 1)

    def refresh_radiobuttons(self):
        """Recreates the radio buttons after updating the data in Settings."""
        self.image_radiobuttons()  # Call your method to recreate the radio buttons

    def get_selected_image(self):
        """Track the selected radio button."""
        selected_number = None  # Variable to store the selected radio button number
        n_types= len(self.table_vars.items())
        # Iterate over all radio buttons
        for number, radio_button in self.table_vars.items():

            if radio_button.isChecked():
                selected_number = number  # Track the currently selected radio button

        if selected_number is not None:
            self.selected_image = selected_number  # Store the selected option for further use
            return self.selected_image, n_types

    def create_radiobuttons(self):
        """Create radio buttons for tools and a settings button."""

        # Create a QGroupBox for "Functions (Wafer)"
        frame = QGroupBox("Functions (Wafer)")
        frame.setStyleSheet(GROUP_BOX_STYLE)

        frame_layout = QGridLayout(frame)

        # Add radio buttons to the frame layout
        frame_layout.addWidget(self.split_rename, 0, 0)
        frame_layout.addWidget(self.rename, 1, 0)
        frame_layout.addWidget(self.clean, 2, 0)
        frame_layout.setContentsMargins(5, 20, 5, 5)
        # Add the frame to the main layout
        self.layout.addWidget(frame, 0, 2)  # Add frame to main layout

        # Add buttons to the shared button group
        self.button_group.addButton(self.split_rename)
        self.button_group.addButton(self.rename)
        self.button_group.addButton(self.clean)

    def create_radiobuttons_all(self):
        """Create radio buttons for tools and a settings button."""

        # Create a QGroupBox for "Functions (Lot)"
        frame = QGroupBox("Functions (Lot)")
        frame.setStyleSheet(GROUP_BOX_STYLE)

        frame_layout = QGridLayout(frame)

        # Add radio buttons to the frame layout
        frame_layout.addWidget(self.split_rename_all, 0, 0)
        frame_layout.addWidget(self.rename_all, 1, 0)
        frame_layout.addWidget(self.clean_all, 2, 0)

        frame_layout.setContentsMargins(5, 20, 5, 5)
        # Add the frame to the main layout
        self.layout.addWidget(frame, 0, 3)  # Add frame to main layout

        # Add buttons to the shared button group
        self.button_group.addButton(self.split_rename_all)
        self.button_group.addButton(self.rename_all)
        self.button_group.addButton(self.clean_all)

    
    def create_radiobuttons_other(self):
        """Create radio buttons for tools and a settings button."""

        # Create a QGroupBox for "Functions (Other)"
        frame = QGroupBox("Functions (Other)")
        frame.setStyleSheet(GROUP_BOX_STYLE)

        frame_layout = QGridLayout(frame)

        # Add radio buttons to the frame layout
        frame_layout.addWidget(self.create_folder, 0, 0)
        frame_layout.setContentsMargins(5, 20, 5, 5)

        # Add the frame to the main layout
        self.layout.addWidget(frame, 0, 1)  # Add frame to main layout

        # Add buttons to the shared button group
        self.button_group.addButton(self.create_folder)

    def select_folder(self):
        """Select a parent folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select a Folder")

        if folder:
            self.dirname = folder
            max_characters = 20  # Set character limit

            # Truncate text if it exceeds the limit
            display_text = self.dirname if len(
                self.dirname) <= max_characters else self.dirname[
                                                     :max_characters] + '...'
            self.folder_path_label.setText(display_text)

    def create_run_button(self):
        """Create a button to run data processing"""

        # Create the QPushButton
        run_button = QPushButton("Run function")
        run_button.setStyleSheet(RUN_BUTTON_STYLE)
        run_button.setFixedWidth(150)
        run_button.clicked.connect(self.run_data_processing)

        # Add the button to the layout at position (0, 3)
        self.layout.addWidget(run_button, 0, 5)

    def run_data_processing(self):
        """Handles photoluminescence data processing and updates progress."""

        scale_data = self.new_folder + os.sep + "settings_data.json"
        wafer_number= self.get_selected_option()


        if not self.dirname or not any([self.rename.isChecked()
                                        or not self.clean.isChecked()
                                        or not self.split_rename.isChecked()
                                        or not self.rename_all.isChecked()
                                        or not self.clean_all.isChecked()
                                        or not self.split_rename_all.isChecked()
                                        ]):
            return

        # Initialize processing classes
        sem_class = Process(self.dirname, wafer=wafer_number, scale = scale_data)
        total_steps = 0
        if self.split_rename.isChecked():
            total_steps = 3
        if self.rename.isChecked():
            total_steps = 1
        if self.clean.isChecked():
            total_steps = 1

        if self.split_rename_all.isChecked():
            total_steps = 3
        if self.rename_all.isChecked():
            total_steps = 1
        if self.clean_all.isChecked():
            total_steps = 1
        if self.create_folder.isChecked():
            total_steps = 1


        progress_dialog = QProgressDialog("Data processing in progress...",
                                          "Cancel", 0, total_steps, self)

        font = QFont()
        font.setPointSize(20)  # Set the font size to 14
        # (or any size you prefer)
        progress_dialog.setFont(font)

        progress_dialog.setWindowTitle("Processing")
        progress_dialog.setWindowModality(Qt.ApplicationModal)
        progress_dialog.setAutoClose(
            False)  # Ensure the dialog is not closed automatically
        progress_dialog.setCancelButton(None)  # Hide the cancel button
        progress_dialog.resize(400, 150)  # Set a larger size for the dialog

        progress_dialog.show()

        QApplication.processEvents()

        def execute_with_timer(task_name, task_function, *args, **kwargs):
            """Executes a task and displays the time taken."""
            start_time = time.time()
            progress_dialog.setLabelText(task_name)
            QApplication.processEvents()  # Ensures the interface is updated
            task_function(*args, **kwargs)
            elapsed_time = time.time() - start_time
            print(f"{task_name} completed in {elapsed_time:.2f} seconds.")

        if self.split_rename.isChecked():
            execute_with_timer("Cleaning of folders", sem_class.clean)
            execute_with_timer("Create folders",
                               sem_class.organize_and_rename_files)

            execute_with_timer("Split w/ tag", sem_class.split_tiff)
            execute_with_timer("Rename w/ tag", sem_class.rename)
            self.update_wafer()

        if self.split_rename_all.isChecked():
            execute_with_timer("Cleaning of folders", sem_class.clean_all)
            execute_with_timer("Create folders",
                               sem_class.organize_and_rename_files)

            execute_with_timer("Split w/ tag", sem_class.split_tiff_all)
            execute_with_timer("Rename w/ tag", sem_class.rename_all)
            self.update_wafer()

        if self.rename_all.isChecked():
            execute_with_timer("Rename files w/o tag", sem_class.clean_folders_and_files)
            execute_with_timer("Create folders", sem_class.organize_and_rename_files)
            self.update_wafer()
            execute_with_timer("Rename files w/o tag", sem_class.rename_wo_legend_all)

        if self.rename.isChecked():
            execute_with_timer("Rename files w/o tag", sem_class.clean_folders_and_files)
            execute_with_timer("Create folders", sem_class.organize_and_rename_files)
            self.update_wafer()
            execute_with_timer("Rename files w/o tag", sem_class.rename_wo_legend)

        if self.clean.isChecked():
            execute_with_timer("Cleaning of folders", sem_class.clean)

        if self.clean_all.isChecked():
            execute_with_timer("Cleaning of folders", sem_class.clean_all)

        if self.create_folder.isChecked():
            execute_with_timer("Create folders", sem_class.organize_and_rename_files)
            self.update_wafer()

        progress_dialog.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings_window = SettingsWindow()
    settings_window.show()
    sys.exit(app.exec_())
