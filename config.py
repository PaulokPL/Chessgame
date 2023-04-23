import time
from PyQt5.QtCore import QPointF, QCoreApplication, QTime
from PyQt5.QtWidgets import QDialog, QFormLayout, QInputDialog, QRadioButton, QLineEdit, QPushButton, QMessageBox
import sqlite3
import xml.etree.ElementTree as ET

class ConfigDialog(QDialog):
    def __init__(self, chessboard, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setModal(True)
        self.initUI()
        self.chessboard = chessboard
        self.move_history = self.chessboard.move_history
        self.ip = self.chessboard.ip
        self.port = self.chessboard.port

    def initUI(self):
        layout = QFormLayout(self)

        save_history_button = QPushButton("Save Game History in SQL")
        save_history_button.clicked.connect(self.save_history)
        load_history_button = QPushButton("Load Game History in SQL")
        load_history_button.clicked.connect(self.load_history)
        layout.addRow(save_history_button, load_history_button)

        save_history_button_xml = QPushButton("Save Game History in XML")
        save_history_button_xml.clicked.connect(self.save_history_xml)
        load_history_button_xml = QPushButton("Load Game History in XML")
        load_history_button_xml.clicked.connect(self.load_history_xml)
        layout.addRow(save_history_button_xml, load_history_button_xml)

    def save_history(self):
        conn = sqlite3.connect("game_history.db")
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS games
                         (id INTEGER PRIMARY KEY, mode TEXT, ip_address TEXT, port TEXT)''')

        c.execute("INSERT INTO games (mode, ip_address, port) VALUES (?, ?, ?)",
                  (self.chessboard.game_mode, self.ip, self.port))
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
        mode.text = self.chessboard.game_mode

        ip_address = ET.SubElement(root, "ip_address")
        ip_address.text = self.ip

        port = ET.SubElement(root, "port")
        port.text = self.port

        moves = ET.SubElement(root, "moves")
        for move in self.move_history:
            ET.SubElement(moves, "move").text = move

        tree = ET.ElementTree(root)
        tree.write("game_history.xml")

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

        conn.close()

        if not moves:
            QMessageBox.warning(self, "Error", "No moves found for the selected game.")
            return

        self.chessboard.set_scene()

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
                            self.chessboard.black_move = True
                            self.chessboard.white_clock = False
                            self.chessboard.analog_clock.is_running = False
                            self.chessboard.analog_clock2.is_running = True
                            self.chessboard.label.setText("Black move")
                        else:
                            self.chessboard.current_player = "white"
                            self.chessboard.white_move = True
                            self.chessboard.black_clock = False
                            self.chessboard.analog_clock2.is_running = False
                            self.chessboard.analog_clock.is_running = True
                            self.chessboard.label.setText("White move")
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

    def load_history_xml(self):
        tree = ET.parse('game_history.xml')
        root = tree.getroot()

        moves = root.find('moves').findall('move')
        self.chessboard.set_scene()

        for move in moves:
            move_str = move.text
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
                            self.chessboard.black_move = True
                            self.chessboard.white_clock = False
                            self.chessboard.analog_clock.is_running = False
                            self.chessboard.analog_clock2.is_running = True
                            self.chessboard.label.setText("Black move")
                        else:
                            self.chessboard.current_player = "white"
                            self.chessboard.white_move = True
                            self.chessboard.black_clock = False
                            self.chessboard.analog_clock2.is_running = False
                            self.chessboard.analog_clock.is_running = True
                            self.chessboard.label.setText("White move")
            time.sleep(0.5)
            QCoreApplication.processEvents()