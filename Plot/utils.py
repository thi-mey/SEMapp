"""
Utility functions for frame management and screenshot functionality.

This module provides functions to create save buttons and manage frame layouts
in the application. It includes functionality for capturing and saving
combined screenshots of multiple frames.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter

# Style constants
SAVE_BUTTON_STYLE = """
    QPushButton {
        font-size: 16px;
        background-color: #e1bee7;
        border: 2px solid #8c8c8c;
        border-radius: 10px;
        padding: 5px;
        height: 20px;
    }
    QPushButton:hover {
        background-color: #ce93d8;
    }
"""

BUTTON_POSITION = {
    'row': 4,
    'column': 0,
    'row_span': 1,
    'column_span': 6
}


def create_savebutton(layout, frame_left, frame_right):
    """
    Create a save button to capture and save specific frames as a combined image.

    Args:
        layout: The layout where the save button will be added
        frame_left: The left frame to capture
        frame_right: The right frame to capture

    Returns:
        None
    """
    def save_image():
        """
        Capture and save specific frames as a combined image.

        Creates a screenshot of both left and right frames, combines them
        horizontally and saves the result as a PNG file.
        """
        screen_left = frame_left.grab()
        screen_right = frame_right.grab()

        file_name, _ = QFileDialog.getSaveFileName(
            parent=None,
            caption="Save screenshot",
            directory="",
            filter="PNG Files (*.png);;All Files (*)"
        )

        if file_name:
            combined_width = screen_left.width() + screen_right.width()
            combined_height = max(screen_left.height(), screen_right.height())
            combined_pixmap = QPixmap(combined_width, combined_height)

            # Fill the combined QPixmap with a white background
            combined_pixmap.fill(Qt.white)

            painter = QPainter(combined_pixmap)
            painter.drawPixmap(0, 0, screen_left)
            painter.drawPixmap(screen_left.width(), 0, screen_right)
            painter.end()

            # Save the combined image
            combined_pixmap.save(file_name, "PNG")

    # Create and configure the save button
    save_button = QPushButton("Screenshot")
    save_button.setStyleSheet(SAVE_BUTTON_STYLE)
    save_button.clicked.connect(save_image)
    
    # Add the button to the layout using position constants
    layout.addWidget(
        save_button,
        BUTTON_POSITION['row'],
        BUTTON_POSITION['column'],
        BUTTON_POSITION['row_span'],
        BUTTON_POSITION['column_span']
    )
