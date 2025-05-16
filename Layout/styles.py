"""Module containing all styles for the GUI"""

# Radio button styles
RADIO_BUTTON_STYLE = """
    QRadioButton {
        spacing: 0px;
        font-size: 14px;
    }
    QRadioButton::indicator {
        width: 20px;
        height: 20px;
    }
    QRadioButton::indicator:checked {
        background-color: #f0ca41;
        border: 2px solid black;
    }
    QRadioButton::indicator:unchecked {
        background-color: white;
        border: 2px solid #ccc;
    }
"""

# Settings button style
SETTINGS_BUTTON_STYLE = """
    QPushButton {
        font-size: 16px;
        background-color: #b3e5fc; 
        border: 2px solid #8c8c8c;
        border-radius: 10px;
        padding: 5px;
        height: 100px;
    }
    QPushButton:hover {
        background-color: #64b5f6; 
    }
"""

# Run button style
RUN_BUTTON_STYLE = """
    QPushButton {
        font-size: 16px;
        background-color: #ffcc80;
        border: 2px solid #8c8c8c;
        border-radius: 10px;
        padding: 5px;
        height: 100px;
    }
    QPushButton:hover {
        background-color: #ffb74d;
    }
"""

# Group box style
GROUP_BOX_STYLE = """
    QGroupBox {
        border: 1px solid black;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 20px;
        font-weight: bold;
    }
    QGroupBox::title {
        font-size: 14px; 
        font-weight: bold;
        subcontrol-origin: margin;
        subcontrol-position: top center;
    }
"""

# Wafer button styles
WAFER_BUTTON_DEFAULT_STYLE = """
    QRadioButton {
        spacing: 0px;
        font-size: 16px;
    }
    QRadioButton::indicator {
        width: 25px;
        height: 25px;
    }
    QRadioButton::indicator:checked {
        background-color: #ccffcc;
        border: 2px solid black;
    }
    QRadioButton::indicator:unchecked {
        background-color: white;
        border: 2px solid #ccc;
    }
"""

WAFER_BUTTON_EXISTING_STYLE = """
    QRadioButton {
        spacing: 0px;
        font-size: 16px;
    }
    QRadioButton::indicator {
        width: 25px;
        height: 25px;
        border: 2px solid #ccc;
        background-color: lightblue;
    }
    QRadioButton::indicator:checked {
        background-color: #ccffcc;
        border: 2px solid black;
    }
    QRadioButton::indicator:unchecked {
        background-color: lightblue;
        border: 2px solid #ccc;
    }
"""

WAFER_BUTTON_MISSING_STYLE = """
    QRadioButton {
        spacing: 0px;
        font-size: 16px;
    }
    QRadioButton::indicator {
        width: 25px;
        height: 25px;
        border: 2px solid #ccc;
        background-color: lightcoral;
    }
    QRadioButton::indicator:checked {
        background-color: #ccffcc;
        border: 2px solid black;
    }
    QRadioButton::indicator:unchecked {
        background-color: lightcoral;
        border: 2px solid #ccc;
    }
"""

# Style pour les boutons de sélection de dossier/fichier
SELECT_BUTTON_STYLE = """
    QPushButton {
        font-size: 16px;
        background-color: #b3e5fc; 
        border: 2px solid #8c8c8c;
        border-radius: 10px; 
        padding: 10px;
    }
    QPushButton:hover {
        background-color: #64b5f6; 
    }
"""

# Style pour les labels de chemin
PATH_LABEL_STYLE = """
    QLabel {
        font-size: 14px;
        padding: 5px;
    }
""" 