"""Styles definitions for the GUI components."""

# Button styles
OPEN_BUTTON_STYLE = """
    QPushButton {
        font-size: 16px;
        background-color: #ffcc80;
        border: 2px solid #8c8c8c;
        border-radius: 10px;
        padding: 5px;
        height: 50px;
    }
    QPushButton:hover {
        background-color: #ffb74d;
    }
"""

# Message box styles
MESSAGE_BOX_STYLE = """
    QMessageBox {
        background-color: white;
    }
    QMessageBox QLabel {
        color: #333;
        font-size: 14px;
    }
    QPushButton {
        background-color: #ffcc80;
        border: 2px solid #8c8c8c;
        border-radius: 5px;
        padding: 5px 15px;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #ffb74d;
    }
"""

# Frame styles
FRAME_STYLE = "background-color: white;" 