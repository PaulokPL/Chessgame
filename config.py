import sys
import time

from PySide2.QtCore import Qt, QSettings, QPointF
from PySide2.QtWidgets import QApplication, QDialog, QFormLayout,QVBoxLayout, QListWidget, QInputDialog, QRadioButton, QLineEdit, QPushButton, QMessageBox
from PySide2.QtGui import QIntValidator
import sqlite3
import json
import xml.etree.ElementTree as ET
from PySide2.QtCore import QThread, QCoreApplication

class ConfigDialog(QDialog):
    def __init__(self, move_history, chessboard, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setModal(True)
        self.initUI()
        self.move_history = move_history
        self.chessboard = chessboard

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

        self.ip_input.setInputMask("000.000.000.000;_")
        # self.ip_input.setValidator(QIntValidator(0, 255, self))
        self.port_input = QLineEdit()
        self.port_input.setInputMask("00000")
        layout.addRow("IP address:", self.ip_input)
        layout.addRow("Port:", self.port_input)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addRow(ok_button)

        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_config)
        load_button = QPushButton("Load Configuration")
        load_button.clicked.connect(self.load_config)
        layout.addRow(save_button, load_button)

        save_history_button = QPushButton("Save Game History in SQL")
        save_history_button.clicked.connect(self.save_history)
        load_history_button = QPushButton("Load Game History in SQL")
        load_history_button.clicked.connect(self.load_history)
        layout.addRow(save_history_button, load_history_button)

        save_history_buttonxml = QPushButton("Save Game History in XML")
        save_history_buttonxml.clicked.connect(self.save_history_xml)
        load_history_buttonxml = QPushButton("Load Game History")
        # load_history_button.clicked.connect(self.load_history)
        layout.addRow(save_history_buttonxml, load_history_buttonxml)

    def on_radio_button_toggle(self, button):
        if button.isChecked():
            self.game_mode = button.text()

    # def save_config(self):
    #     settings = QSettings("MyApp", "MyGame")
    #     settings.setValue("game_mode", self.game_mode)
    #     settings.setValue("ip_address", self.ip_input.text())
    #     settings.setValue("port", self.port_input.text())
    #     QMessageBox.information(self, "Saved", "Configuration saved successfully.")
    #
    # def load_config(self):
    #     settings = QSettings("MyApp", "MyGame")
    #     game_mode = settings.value("game_mode", "1 player")
    #     if game_mode == "1 player":
    #         self.player_radio.setChecked(True)
    #     elif game_mode == "2 player":
    #         self.two_player_radio.setChecked(True)
    #     elif game_mode == "AI":
    #         self.ai_radio.setChecked(True)
    #     self.ip_input.setText(settings.value("ip_address", ""))
    #     self.port_input.setText(settings.value("port", ""))
    #     QMessageBox.information(self, "Loaded", "Configuration loaded successfully.")

    def save_history(self):
        conn = sqlite3.connect("game_history.db")
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS games
                         (id INTEGER PRIMARY KEY, mode TEXT, ip_address TEXT, port TEXT)''')

        c.execute("INSERT INTO games (mode, ip_address, port) VALUES (?, ?, ?)",
                  (self.game_mode, self.ip_input.text(), self.port_input.text()))
        game_id = c.lastrowid

        c.execute('''CREATE TABLE IF NOT EXISTS moves
                         (id INTEGER PRIMARY KEY, game_id INTEGER, move_number INTEGER, move_data TEXT,
                          FOREIGN KEY (game_id) REFERENCES games(id))''')

        for i, move in enumerate(self.move_history):
            c.execute("INSERT INTO moves (game_id, move_number, move_data) VALUES (?, ?, ?)",
                      (game_id, i + 1, str(move)))

        conn.commit()
        conn.close()
    def save_history_xml(self):
        root = ET.Element("game_history")

        mode = ET.SubElement(root, "mode")
        mode.text = self.game_mode

        ip_address = ET.SubElement(root, "ip_address")
        ip_address.text = self.ip_input.text()

        port = ET.SubElement(root, "port")
        port.text = self.port_input.text()

        moves = ET.SubElement(root, "moves")
        for move in self.move_history:
            ET.SubElement(moves, "move").text = move

        tree = ET.ElementTree(root)
        tree.write("game_history.xml")

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

    def load_history(self):
        conn = sqlite3.connect("game_history.db")
        c = conn.cursor()

        c.execute("SELECT * FROM games ORDER BY id DESC LIMIT 10")
        games = c.fetchall()

        if not games:
            QMessageBox.warning(self, "Error", "No game history found.")
            return

        game_items = []
        for game in games:
            game_id, game_mode, ip_address, port = game
            game_items.append(f"ID: {game_id} | Mode: {game_mode} | IP: {ip_address} | Port: {port}")

        selected_game, ok = QInputDialog.getItem(self, "Select game", "Select a game to play back:", game_items, 0,
                                                 False)
        if not ok:
            return

        game_id = int(selected_game.split(":")[1].split("|")[0].strip())

        c.execute("SELECT move_data FROM moves WHERE game_id = ? ORDER BY move_number", (game_id,))
        moves = c.fetchall()


        # moves_str = "".join(moves)
        conn.close()

        if not moves:
            QMessageBox.warning(self, "Error", "No moves found for the selected game.")
            return

        self.chessboard.set_scene()
        movement = []
        for move in moves:
            move_str = "".join(move)
            file_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
            rank_map = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
            x_s = file_map[move_str[0]] * self.chessboard.square_size
            y_s = rank_map[move_str[1]] * self.chessboard.square_size
            x_d = file_map[move_str[2]] * self.chessboard.square_size
            y_d = rank_map[move_str[3]] * self.chessboard.square_size
            new_tuple_src = tuple((x_s, y_s))
            new_tuple_dst = tuple((x_d, y_d))
            new_tuple_dst_10 = tuple((x_d + 10, y_d + 10))
            src_square = self.chessboard.items(QPointF(*new_tuple_src))
            dst_square = self.chessboard.items(QPointF(*new_tuple_dst_10))
            piece = src_square[0].piece
            if piece is not None:
                if piece.color == self.chessboard.current_player:
                    piece.possible_moves = piece.moves_continue()
                    if new_tuple_dst in piece.possible_moves:
                        piece.application_movement(QPointF(*new_tuple_dst), dst_square[0])
                        if self.chessboard.current_player == "white":
                            self.chessboard.current_player = "black"
                        else:
                            self.chessboard.current_player = "white"
            time.sleep(0.5)
            QCoreApplication.processEvents()
        # replay_dialog = QDialog(self)
        # replay_dialog.setWindowTitle("Game History")
        # replay_dialog.setModal(True)
        # replay_dialog.resize(400, 400)
        #
        # replay_layout = QVBoxLayout(replay_dialog)
        # move_list = QListWidget()
        # replay_layout.addWidget(move_list)
        #
        # for move in moves:
        #     move_list.addItem(move[0])
        #
        # replay_dialog.exec_()