import sys
from PySide2.QtCore import Qt, QSettings
from PySide2.QtWidgets import QApplication, QDialog, QFormLayout, QRadioButton, QLineEdit, QPushButton, QMessageBox
import sqlite3
import json
import xml.etree.ElementTree as ET


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        # self.setModal(True)
        self.initUI()

    def initUI(self):
        # Create layout for the dialog
        layout = QFormLayout(self)

        # Add radio buttons for game mode
        self.game_mode = "1 player"  # default value
        self.player_radio = QRadioButton("1 player")
        self.player_radio.toggled.connect(lambda: self.on_radio_button_toggle(self.player_radio))
        self.player_radio.setChecked(True)
        self.two_player_radio = QRadioButton("2 player")
        self.two_player_radio.toggled.connect(lambda: self.on_radio_button_toggle(self.two_player_radio))
        self.ai_radio = QRadioButton("AI")
        self.ai_radio.toggled.connect(lambda: self.on_radio_button_toggle(self.ai_radio))
        layout.addRow("Game mode:", self.player_radio)
        layout.addRow("", self.two_player_radio)
        layout.addRow("", self.ai_radio)

        # Add input for IP address and port
        self.ip_input = QLineEdit()
        self.ip_input.setInputMask("000.000.000.000;_")
        self.port_input = QLineEdit()
        self.port_input.setInputMask("00000")
        layout.addRow("IP address:", self.ip_input)
        layout.addRow("Port:", self.port_input)

        # Add buttons for saving and loading configurations
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_config)
        load_button = QPushButton("Load Configuration")
        load_button.clicked.connect(self.load_config)
        layout.addRow(save_button, load_button)

        # Add buttons for saving and loading game history
        save_history_button = QPushButton("Save Game History")
        # save_history_button.clicked.connect(self.save_history)
        load_history_button = QPushButton("Load Game History")
        # load_history_button.clicked.connect(self.load_history)
        layout.addRow(save_history_button, load_history_button)

    def on_radio_button_toggle(self, button):
        if button.isChecked():
            self.game_mode = button.text()

    def save_config(self):
        settings = QSettings("MyApp", "MyGame")
        settings.setValue("game_mode", self.game_mode)
        settings.setValue("ip_address", self.ip_input.text())
        settings.setValue("port", self.port_input.text())
        QMessageBox.information(self, "Saved", "Configuration saved successfully.")

    def load_config(self):
        settings = QSettings("MyApp", "MyGame")
        game_mode = settings.value("game_mode", "1 player")
        if game_mode == "1 player":
            self.player_radio.setChecked(True)
        elif game_mode == "2 player":
            self.two_player_radio.setChecked(True)
        elif game_mode == "AI":
            self.ai_radio.setChecked(True)
        self.ip_input.setText(settings.value("ip_address", ""))
        self.port_input.setText(settings.value("port", ""))
        QMessageBox.information(self, "Loaded", "Configuration loaded successfully.")

    # def save_history(self):
    #     conn = sqlite3.connect("game_history.db")
    #     c = conn.cursor()
    #     c.execute('''CREATE TABLE IF NOT EXISTS game_history
    #                  (id INTEGER PRIMARY KEY, mode TEXT, ip_address TEXT, port TEXT, moves TEXT)''')
    #     c.execute("INSERT INTO game_history (mode, ip_address, port, moves) VALUES (?, ?, ?, ?)",
    #               (self.game_mode