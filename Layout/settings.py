"""Module for settings window"""
# pylint: disable=no-name-in-module, trailing-whitespace, too-many-branches, too-many-statements
import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QPushButton,
    QTableWidgetItem
)
from PyQt5.QtCore import pyqtSignal

class SettingsWindow(QDialog):
    """Class for settings window"""
    data_updated = pyqtSignal()  # Signal emitted when data is updated

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")

        # Get the user's folder path (C:\Users\XXXXX)
        self.user_folder = os.path.expanduser("~")

        # Define the new folder "SEM" and the file to store settings
        self.new_folder = os.path.join(self.user_folder, "SEM")
        self.data_file = os.path.join(self.new_folder, "settings_data.json")
        self.data = []  # Structure to store the table data

        # Set up the UI layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create and add the table and buttons to the layout
        self.create_table()
        self.create_buttons()

        # Load data from the settings file
        self.load_data()

    def create_table(self):
        """Create the settings table."""
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Scale", "Image Type"])

        # Temporarily block signals to prevent updates during initialization
        self.table.blockSignals(True)

        # Populate the table with existing data
        for row_data in self.data:
            if "Scale" in row_data and "Image Type" in row_data:
                self.add_row(row_data["Scale"], row_data["Image Type"], update_data=False)
            else:
                print(f"Invalid row data: {row_data}")

        # Re-enable signals after table population
        self.table.blockSignals(False)

        # Connect the itemChanged signal to update the data structure
        self.table.itemChanged.connect(self.update_data)
        self.layout.addWidget(self.table)

    def create_buttons(self):
        """Create buttons to add and remove rows."""
        add_button = QPushButton("Add Row")
        remove_button = QPushButton("Remove Selected Row")

        add_button.clicked.connect(self.add_row)
        remove_button.clicked.connect(self.remove_selected_row)

        self.layout.addWidget(add_button)
        self.layout.addWidget(remove_button)

    def add_row(self, scale="5x5", image_type="Type", update_data=True):
        """Add a new row to the table with default values."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        scale_item = QTableWidgetItem(scale)
        image_type_item = QTableWidgetItem(image_type)

        self.table.setItem(row_position, 0, scale_item)
        self.table.setItem(row_position, 1, image_type_item)

        if update_data:
            self.data.append({"Scale": scale, "Image Type": image_type})
            print("Row added:", self.data)

    def remove_selected_row(self):
        """Remove the currently selected row from the table."""
        current_row = self.table.currentRow()
        if current_row != -1:
            self.table.removeRow(current_row)
            del self.data[current_row]
            print("Row removed:", self.data)

    def update_data(self, item):
        """Update the data structure when a cell value changes."""
        try:
            row = item.row()
            column = item.column()
            value = item.text().strip()

            while len(self.data) <= row:
                self.data.append({"Scale": "", "Image Type": ""})

            if column == 0:  # Update "Scale"
                if not value.replace('.', '', 1).isdigit():
                    print(f"Invalid value for Scale: {value}")
                    return
                self.data[row]["Scale"] = value
            elif column == 1:  # Update "Image Type"
                self.data[row]["Image Type"] = value
            else:
                print(f"Unexpected column index: {column}")
                return

            self.save_data()
            print(f"Data updated successfully: {self.data[row]}")
        except Exception as e:
            print(f"Error updating data: {e}")

    def closeEvent(self, event):
        """Save data to a file when the dialog is closed."""
        self.save_data()
        self.data_updated.emit()
        super().closeEvent(event)

    def normalize_data(self):
        """Synchronize self.data with the actual table contents."""
        self.data = self.get_table_data()

    def save_data(self):
        """Save the table data to a JSON file."""
        self.normalize_data()
        with open(self.data_file, "w") as file:
            json.dump(self.data, file, indent=4)
        print("Data saved successfully.")

    def load_data(self):
        """Load the table data from the JSON file."""
        try:
            with open(self.data_file, "r") as file:
                self.data = json.load(file)
            print("Data loaded successfully:", self.data)
        except FileNotFoundError:
            print("No previous data found. Starting fresh.")
            self.data = []
        except Exception as err:
            print(f"Error loading data: {err}")
            self.data = []

        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for row_data in self.data:
            self.add_row(row_data.get("Scale", ""),
                        row_data.get("Image Type", ""), update_data=False)
        self.table.blockSignals(False)

    def get_table_data(self):
        """Get the current data from the table as a list of dictionaries."""
        table_data = []
        for row in range(self.table.rowCount()):
            scale_item = self.table.item(row, 0)
            image_type_item = self.table.item(row, 1)

            if scale_item and image_type_item:
                scale = scale_item.text()
                image_type = image_type_item.text()
                table_data.append({"Scale": scale, "Image Type": image_type})

        return table_data 
