"""
GUI for data visualization.

This module implements the main window and core functionality
for the SEM data visualization application.
"""

import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from semapp.Layout.main_window_att import LayoutFrame
from semapp.Layout.create_button import ButtonFrame
from semapp.Plot.frame_attributes import PlotFrame

# Constants
TIMER_INTERVAL = 200  # Milliseconds
BACKGROUND_COLOR = "#F5F5F5"


class MainWindow(QWidget):  # pylint: disable=R0903
    """
    Main window for data visualization.
    
    This class handles the main application window and initializes all UI components.
    It manages the layout, plotting area, and button controls for the application.
    
    Attributes:
        canvas_widget (QWidget): The main widget container
        canvas_layout (QGridLayout): The main layout manager
        layout_frame (LayoutFrame): Handles layout configuration
        button_frame (ButtonFrame): Contains all button controls
        plot_frame (PlotFrame): Manages the plotting area
        timer (QTimer): Updates the scroll area size
    """

    def __init__(self):
        """Initialize the main window and UI components."""
        super().__init__()
        self.canvas_widget = None
        self.canvas_layout = None
        self.layout_frame = None
        self.button_frame = None
        self.plot_frame = None
        self.timer = None
        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface.
        
        Sets up the window properties, layouts, and all UI components.
        Configures the main layout, creates frames for different sections,
        and initializes the update timer.
        """
        self.setWindowTitle("Data Visualization")
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        # Create the main layout (canvas_layout)
        self.canvas_widget = QWidget(self)
        self.canvas_layout = QGridLayout(self.canvas_widget)

        # Use LayoutFrame for layout configuration
        self.layout_frame = LayoutFrame(self)
        self.layout_frame.setup_layout(self.canvas_widget, self.canvas_layout)

        self.button_frame = ButtonFrame(self.canvas_layout)
        self.plot_frame = PlotFrame(self.canvas_layout, self.button_frame)

        # Set/adapt the maximum window size
        self.layout_frame.set_max_window_size()
        self.layout_frame.position_window_top_left()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.layout_frame.adjust_scroll_area_size)
        self.timer.start(TIMER_INTERVAL)


def main():
    print("SEMapp launched")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
