from PyQt5.QtWidgets import QDialog, QFormLayout, QInputDialog, QRadioButton, QLineEdit, QPushButton, QMessageBox
import json
class ConfigDialogIP(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setModal(True)
        self.initUI()
        self.game_mode = "1 player"
        self.ip = "192"
        self.port = "1024"

    def initUI(self):
        layout = QFormLayout(self)

        self.game_mode = "1 player"
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

        self.ip_input = QLineEdit()
        self.ip_input.setInputMask("HHHH:HHHH:HHHH:HHHH:HHHH:HHHH:HHHH:HHHH;_")
        # self.ip_input.setInputMask("000.000.000.000;_")

        # self.ip_input.textChanged.connect(self.check_ip)
        self.port_input = QLineEdit()
        self.port_input.setInputMask("00000")
        layout.addRow("IP address:", self.ip_input)
        layout.addRow("Port:", self.port_input)



        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_config)
        load_button = QPushButton("Load Configuration")
        load_button.clicked.connect(self.load_config)
        layout.addRow(save_button, load_button)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept_button)
        layout.addRow(ok_button)
    # def check_ip(self, text):
    #     parts = text.split('.')
    #     for part in parts:
    #         if part != '':
    #             if int(part)>255:
    #                 QMessageBox.warning(self, "Error", "Invalid IP address!")
    #                 self.ip_input.clear()
    #                 break

    def accept_button(self):
        self.ip = self.ip_input.text()
        self.port = self.port_input.text()
        self.accept()

    def on_radio_button_toggle(self, button):
        if button.isChecked():
            self.game_mode = button.text()

    def save_config(self):
        config = {
            "game_mode": self.game_mode,
            "ip_address": self.ip_input.text(),
            "port": self.port_input.text()
        }
        with open("config.json", "w") as f:
            json.dump(config, f)
        QMessageBox.information(self, "Saved", "Configuration saved successfully.")

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            game_mode = config.get("game_mode", "1 player")
            if game_mode == "1 player":
                self.player_radio.setChecked(True)
            elif game_mode == "2 player":
                self.two_player_radio.setChecked(True)
            elif game_mode == "AI":
                self.ai_radio.setChecked(True)
            self.ip_input.setText(config.get("ip_address", ""))
            self.port_input.setText(config.get("port", ""))
            QMessageBox.information(self, "Loaded", "Configuration loaded successfully.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Not Found", "Configuration file not found.")