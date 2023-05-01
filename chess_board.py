import random

from PyQt5.QtCore import QVariant, QTime, QTimer, QMetaObject, Qt, Q_ARG, QPointF, pyqtSlot, QObject
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QResource
from piece import ChessPiece
from chess_square import ChessSquare
from PyQt5.QtWidgets import QGraphicsProxyWidget, QPushButton
from analog_clock import  AnalogClock
from config import ConfigDialog
import time
import socket
import threading
import numpy as np
class ChessBoard(QGraphicsScene):
    def __init__(self, mode, ip, port, parent=None):
        super().__init__(parent)
        self.setSceneRect(-50, -50, 900, 800)
        self.square_size = 80
        self.addRect(-80, -80, 800, 800, QPen(), QBrush(QColor("#c9b18b")))
        self.setBackgroundBrush(QBrush(QColor(162, 164, 168, 255)))
        self.white_pieces = []
        self.move_history = []
        self.game_mode = mode
        self.ip = ip
        self.port = port
        # print(ip,":", port)
        if self.game_mode == "2 player":
            self.client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.client_socket.connect((ip, int(port)))
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()
        self.current_player = "white"
        self.line_edit = QLineEdit()
        self.line_edit.setGeometry(100, 721, 300, 30)
        self.button = QPushButton("Confirm")
        self.button.setGeometry(410, 721, 150, 30)
        self.button.clicked.connect(self.move_piece)
        self.line_edit.returnPressed.connect(self.button.click)
        self.line_edit.returnPressed.connect(self.line_edit.clear)
        self.label = QLabel("White move")
        self.label.setGeometry(800, 300, 150, 30)
        self.label.setStyleSheet("background-color: #a2a4a8;")
        self.label.setFont(QFont("Arial", 15))
        label_proxy = QGraphicsProxyWidget()
        label_proxy.setWidget(self.label)
        self.addItem(label_proxy)
        self.config = QPushButton("Save/Load history")
        self.config.setGeometry(725, -50, 200, 50)
        self.config.clicked.connect(self.config_show)
        config_proxy = QGraphicsProxyWidget()
        config_proxy.setWidget(self.config)
        self.addItem(config_proxy)

        line_edit_proxy = QGraphicsProxyWidget()
        line_edit_proxy.setWidget(self.line_edit)
        self.addItem(line_edit_proxy)
        button_proxy = QGraphicsProxyWidget()
        button_proxy.setWidget(self.button)
        self.addItem(button_proxy)
        self.add_labels()

        self.white_move = True
        self.black_move = False
        self.white_clock = False
        self.black_clock = False
        self.white_king = None
        self.black_king = None

        self.timer = QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update_clock)
        self.clock = QTime(0, 0, 0, 0)
        self.clock2 = QTime(0, 0, 0, 0)
        self.analog_clock = AnalogClock(self.clock)
        self.analog_clock.is_running = True
        self.analog_clock2 = AnalogClock(self.clock2)
        self.addItem(self.analog_clock)
        self.addItem(self.analog_clock2)
        self.analog_clock.setGeometry(750, 400, 200, 200)
        self.analog_clock2.setGeometry(750, 50, 200, 200)
        self.timer.start()

        self.set_scene()
        QResource.registerResource("chess_pieces.qrc")

        self.white_score = 1290
        self.black_score = 1290


    def receive_messages(self):
        while True:
            message = self.client_socket.recv(1024).decode()
            self.move_history.append(message)

            file_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
            rank_map = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
            x_s = file_map[message[0]] * self.square_size
            y_s = rank_map[message[1]] * self.square_size
            x_d = file_map[message[2]] * self.square_size
            y_d = rank_map[message[3]] * self.square_size

            QMetaObject.invokeMethod(self, "function", Qt.QueuedConnection,
                                     Q_ARG(QVariant, x_s),
                                     Q_ARG(QVariant, y_s),
                                     Q_ARG(QVariant, x_d),
                                     Q_ARG(QVariant, y_d)
                                     )
    @pyqtSlot(QVariant, QVariant,QVariant,QVariant)
    def function(self, xs, ys, xd, yd):
        new_tuple_src = tuple((xs, ys))
        new_tuple_dst = tuple((xd, yd))
        new_tuple_dst_10 = tuple((xd + 10, yd + 10))
        src_square = self.items(QPointF(*new_tuple_src))
        dst_square = self.items(QPointF(*new_tuple_dst_10))
        piece = src_square[0].piece
        if piece is not None:
            if piece.color == self.current_player:
                piece.possible_moves = piece.moves_continue()
                if new_tuple_dst in piece.possible_moves:
                    piece.application_movement(QPointF(*new_tuple_dst), dst_square[0])
                    piece.update()
                    if self.current_player == "white":
                        self.current_player = "black"
                        self.black_move = True
                        self.white_clock = False
                        self.analog_clock.is_running = False
                        self.analog_clock2.is_running = True
                        self.label.setText("Black move")
                    else:
                        self.current_player = "white"
                        self.white_move = True
                        self.black_clock = False
                        self.analog_clock2.is_running = False
                        self.analog_clock.is_running = True
                        self.label.setText("White move")

    def send_message(self):
        message = self.move_history[-1]
        self.client_socket.send(message.encode())


    def update_clock(self):
        if self.analog_clock.is_running:
            self.clock = self.clock.addMSecs(1)
            self.analog_clock.update_time(self.clock)
        if self.analog_clock2.is_running:
            self.clock2 = self.clock2.addMSecs(1)
            self.analog_clock2.update_time(self.clock2)

    def change_board_color(self, color1, color2):
        for item in self.items():
            if isinstance(item, ChessSquare):
                if item.color == "white":
                    item.color = color2
                    item.setBrush(QBrush(QColor(item.color)))
                elif item.color == "grey":
                    item.color = color1
                    item.setBrush(QBrush(QColor(item.color)))
                elif item.color == color2:
                    item.color = "white"
                    item.setBrush(QBrush(QColor(item.color)))
                elif item.color == color1:
                    item.color = "grey"
                    item.setBrush(QBrush(QColor(item.color)))

    def add_labels(self):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for i, letter in enumerate(letters):
            text = QGraphicsTextItem(letter)
            text.setFont(QFont("Arial", 16))
            text.setPos(i * 80 + 30, -30)
            self.addItem(text)
            text1 = QGraphicsTextItem(letter)
            text1.setFont(QFont("Arial", 16))
            text1.setPos(i * 80 + 30, 640)
            self.addItem(text1)

        for i in range(8):
            text = QGraphicsTextItem(str(i + 1))
            text.setFont(QFont("Arial", 16))
            text.setPos(-30, (- i * 80 + 585) )
            self.addItem(text)
            text1 = QGraphicsTextItem(str(i + 1))
            text1.setFont(QFont("Arial", 16))
            text1.setPos(650, - i * 80 + 585)
            self.addItem(text1)
    def move_piece(self):
        notation = self.line_edit.text()
        if not notation:
            return
        src = self.parse_notation(notation[:2])
        dst = self.parse_notation(notation[2:])

        new_tuple_src = tuple(val * self.square_size + 10 for val in src)
        new_tuple_dst = tuple(val * self.square_size for val in dst)
        new_tuple_dst_10 = tuple(val * self.square_size + 10 for val in dst)
        src_square = self.items(QPointF(*new_tuple_src))
        dst_square = self.items(QPointF(*new_tuple_dst_10))
        piece = src_square[0].piece
        if piece is not None:
            if piece.color == self.current_player:
                piece.possible_moves = piece.moves_continue()
                if new_tuple_dst in piece.possible_moves:
                    piece.application_movement(QPointF(*new_tuple_dst), dst_square[0])
        self.line_edit.clear()

    def parse_notation(self,notation):
        file_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        rank_map = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}

        if len(notation) != 2:
            raise ValueError("Invalid notation: {}".format(notation))

        file = notation[0]
        rank = notation[1]

        if file not in file_map or rank not in rank_map:
            raise ValueError("Invalid notation: {}".format(notation))
        x = file_map[file]
        y = rank_map[rank]

        return x, y

    def config_show(self):
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        dialog = ConfigDialog(self)
        # dialog.show()
        if dialog.exec_():
            self.game_mode = dialog.game_mode
        #     if option == "AI":
        #         for item in self.items():
        #             if isinstance(item, ChessPiece):
        #                 self.white_pieces.remove(item)
        #                 self.removeItem(item)
        #         self.set_scene()

    def set_scene(self):
        self.white_pieces = []
        for item in self.items():
            if isinstance(item, ChessPiece) or isinstance(item, ChessSquare):
                self.removeItem(item)
        self.clock = QTime(0, 0, 0, 0)
        self.clock2 = QTime(0, 0, 0, 0)
        self.analog_clock.update_time(self.clock)
        self.analog_clock2.update_time(self.clock)
        self.current_player = "white"
        self.label.setText("White move")
        self.analog_clock.is_running = True
        self.analog_clock2.is_running = False
        self.white_move = True
        self.black_move = False
        self.white_clock = False
        self.black_clock = False
        self.white_king = None
        self.black_king = None
        for row in range(8):
            for col in range(8):
                x = col * self.square_size
                y = row * self.square_size

                if (row + col) % 2 == 0:
                    color = "white"
                else:
                    color = "grey"

                square = ChessSquare(x, y, self.square_size, color)
                self.addItem(square)

                if row in [0, 1, 6, 7]:
                    if row in [6, 7]:
                        player = "white"
                        color_piece = "white"
                        if row in [0, 7]:
                            if col == 0 or col == 7:
                                piece_type = "rook"
                                filename = ":/chess_pieces/icons/white_rook.png"
                            elif col == 1 or col == 6:
                                piece_type = "knight"
                                filename = ":/chess_pieces/icons/white_knight.png"
                            elif col == 2 or col == 5:
                                piece_type = "bishop"
                                filename = ":/chess_pieces/icons/white_bishop.png"
                            elif col == 3:
                                piece_type = "queen"
                                filename = ":/chess_pieces/icons/white_queen.png"
                            else:
                                piece_type = "king"
                                filename = ":/chess_pieces/icons/white_king.png"
                        else:
                            piece_type = "pawn"
                            filename = ":/chess_pieces/icons/white_pawn.png"
                    else:
                        player = "black"
                        color_piece = "black"
                        if row in [0, 7]:
                            if col == 0 or col == 7:
                                piece_type = "rook"
                                filename = ":/chess_pieces/icons/black_rook.png"
                            elif col == 1 or col == 6:
                                piece_type = "knight"
                                filename = ":/chess_pieces/icons/black_knight.png"
                            elif col == 2 or col == 5:
                                piece_type = "bishop"
                                filename = ":/chess_pieces/icons/black_bishop.png"
                            elif col == 3:
                                piece_type = "queen"
                                filename = ":/chess_pieces/icons/black_queen.png"
                            else:
                                piece_type = "king"
                                filename = ":/chess_pieces/icons/black_king.png"
                        else:
                            piece_type = "pawn"
                            filename = ":/chess_pieces/icons/black_pawn.png"
                    piece = ChessPiece(x, y, self.square_size, color_piece, player, piece_type, filename)
                    if piece.piece_type == "king":
                        if piece.color == "white":
                            self.white_king = piece
                        else:
                            self.black_king = piece
                    piece.current_square = square
                    square.piece = piece
                    self.addItem(piece)
                    self.white_pieces.append(piece)

    def evaluate(self):
        piece_values = {
            'pawn': 10,
            'knight': 30,
            'bishop': 30,
            'rook': 50,
            'queen': 90,
            'king': 900
        }
        score = 0
        for itemes in self.white_pieces:
            if itemes.color == "black":
                score -= piece_values[itemes.piece_type]
            else:
                score += piece_values[itemes.piece_type]
        return score


    def minimax(self, depth, is_maximizing_player, alpha, beta):
        if depth == 0:
            return self.evaluate(), None, None

        if is_maximizing_player:
            best_move = None
            best_piece = None
            best_score = -float('inf')
            for pieces in self.white_pieces:
                if pieces.color == "white":
                    moves = pieces.moves_continue()
                    for move in moves:
                        if pieces.piece_type == "pawn" and abs(
                                move[0] - pieces.x) > 60 and not pieces.is_square_occupied_TF(move[0], move[1]):
                            if pieces.color == "white":
                                old_xy = [pieces.x, pieces.y]
                                old_square = pieces.current_square
                                pieces.current_square.piece = None
                                new_move = (move[0] + 10, move[1] + 10)
                                squares = self.items(QPointF(*new_move), Qt.IntersectsItemShape)
                                pieces.current_square = squares[0]
                                squares[0].piece = pieces
                                square5 = self.items(QPointF(move[0] + 10, move[1] + 90),
                                                     Qt.IntersectsItemShape)
                                remember = square5[0].piece
                                pieces.x = new_move[0]
                                pieces.y = new_move[1]
                                self.white_pieces.remove(square5[0].piece)
                                square5[0].piece = None
                                score, _, _ = self.minimax(depth - 1, False, alpha, beta)

                                square5[0].piece = remember
                                self.white_pieces.append(square5[0].piece)
                                pieces.current_square.piece = None
                                pieces.current_square = old_square
                                pieces.current_square.piece = pieces
                                pieces.x = old_xy[0]
                                pieces.y = old_xy[1]
                            else:
                                old_xy = [pieces.x, pieces.y]
                                old_square = pieces.current_square
                                pieces.current_square.piece = None
                                new_move = (move[0] + 10, move[1] + 10)
                                squares = self.items(QPointF(*new_move), Qt.IntersectsItemShape)
                                pieces.current_square = squares[0]
                                squares[0].piece = pieces
                                square5 = self.items(QPointF(move[0] + 10, move[1] - 60),
                                                     Qt.IntersectsItemShape)
                                remember = square5[0].piece
                                self.white_pieces.remove(square5[0].piece)
                                square5[0].piece = None
                                pieces.x = new_move[0]
                                pieces.y = new_move[1]
                                score, _, _ = self.minimax(depth - 1, False, alpha, beta)
                                square5[0].piece = remember
                                self.white_pieces.append(square5[0].piece)
                                pieces.current_square.piece = None
                                pieces.current_square = old_square
                                pieces.current_square.piece = pieces
                                pieces.x = old_xy[0]
                                pieces.y = old_xy[1]
                        else:
                            old_xy = [pieces.x, pieces.y]
                            old_square = pieces.current_square
                            pieces.current_square.piece = None
                            new_move = (move[0] + 10, move[1] + 10)
                            squares = self.items(QPointF(*new_move), Qt.IntersectsItemShape)
                            remember_new_square = squares[0].piece
                            pieces.current_square = squares[0]
                            pieces.x = new_move[0]
                            pieces.y = new_move[1]
                            if remember_new_square is not None:
                                self.white_pieces.remove(squares[0].piece)
                            squares[0].piece = pieces
                            score, _, _ = self.minimax(depth - 1, False, alpha, beta)
                            pieces.current_square.piece = None
                            pieces.current_square = old_square
                            pieces.current_square.piece = pieces
                            squares[0].piece = remember_new_square
                            pieces.x = old_xy[0]
                            pieces.y = old_xy[1]
                            if squares[0].piece is not None:
                                self.white_pieces.append(squares[0].piece)
                        if score > best_score:
                            best_score = score
                            best_move = move
                            best_piece = pieces
                        alpha = max(alpha, score)
                        if beta > alpha:
                            break
            return best_score, best_move, best_piece
        else:
            best_move = None
            best_piece = None
            best_score = float('inf')
            for pieces in self.white_pieces:
                if pieces.color == "black":
                    moves = pieces.moves_continue()
                    for move in moves:
                        if pieces.piece_type == "pawn" and abs(
                                move[0] - pieces.x) > 60 and not pieces.is_square_occupied_TF(move[0], move[1]):
                            if pieces.color == "white":
                                old_xy = [pieces.x, pieces.y]
                                old_square = pieces.current_square
                                pieces.current_square.piece = None
                                new_move = (move[0] + 10, move[1] + 10)
                                squares = self.items(QPointF(*new_move), Qt.IntersectsItemShape)
                                pieces.current_square = squares[0]
                                squares[0].piece = pieces
                                pieces.x = new_move[0]
                                pieces.y = new_move[1]
                                square5 = self.items(QPointF(move[0] + 10, move[1] + 90),
                                                     Qt.IntersectsItemShape)
                                remember = square5[0].piece
                                self.white_pieces.remove(square5[0].piece)
                                square5[0].piece = None
                                score, _, _ = self.minimax(depth - 1, True, alpha, beta)
                                square5[0].piece = remember
                                self.white_pieces.append(square5[0].piece)
                                pieces.current_square.piece = None
                                pieces.current_square = old_square
                                pieces.current_square.piece = pieces
                                pieces.x = old_xy[0]
                                pieces.y = old_xy[1]
                            else:
                                old_xy = [pieces.x, pieces.y]
                                old_square = pieces.current_square
                                pieces.current_square.piece = None
                                new_move = (move[0] + 10, move[1] + 10)
                                squares = self.items(QPointF(*new_move), Qt.IntersectsItemShape)
                                pieces.current_square = squares[0]
                                squares[0].piece = pieces
                                pieces.x = new_move[0]
                                pieces.y = new_move[1]
                                square5 = self.items(QPointF(move[0] + 10, move[1] - 60),
                                                     Qt.IntersectsItemShape)
                                remember = square5[0].piece
                                self.white_pieces.remove(square5[0].piece)
                                square5[0].piece = None
                                score, _, _= self.minimax(depth - 1, True, alpha, beta)
                                square5[0].piece = remember
                                self.white_pieces.append(square5[0].piece)
                                pieces.current_square.piece = None
                                pieces.current_square = old_square
                                pieces.current_square.piece = pieces
                                pieces.x = old_xy[0]
                                pieces.y = old_xy[1]
                        else:
                            old_xy = [pieces.x, pieces.y]
                            old_square = pieces.current_square
                            pieces.current_square.piece = None
                            new_move = (move[0] + 10, move[1] + 10)
                            squares = self.items(QPointF(*new_move), Qt.IntersectsItemShape)
                            remember_new_square = squares[0].piece
                            pieces.current_square = squares[0]
                            pieces.x = new_move[0]
                            pieces.y = new_move[1]
                            if remember_new_square is not None:
                                self.white_pieces.remove(squares[0].piece)
                            squares[0].piece = pieces
                            score, _, _= self.minimax(depth - 1, True, alpha, beta)
                            pieces.current_square.piece = None
                            pieces.current_square = old_square
                            pieces.current_square.piece = pieces
                            squares[0].piece = remember_new_square
                            pieces.x = old_xy[0]
                            pieces.y = old_xy[1]
                            if squares[0].piece is not None:
                                self.white_pieces.append(squares[0].piece)
                        if score < best_score:
                            best_score = score
                            best_move = move
                            best_piece = pieces
                        beta = min(beta, score)
                        if beta < alpha:
                            break
            return best_score, best_move, best_piece

    def ai_movement(self):
        best_piece = None
        best_mov = None
        possiblement = []
        actual_score = self.black_score - self.white_score
        _, best_mov, best_piece = self.minimax(3, False, float('-inf'), float('inf'))
        for pieces in self.white_pieces:
            if pieces.color == "black":
                mov = pieces.get_possible_moves(pieces.x, pieces.y)
                if len(mov) != 0:
                    for mo in mov:
                        move_data = (pieces, mo)
                        possiblement.append(move_data)

        if best_mov is None:
            index = random.choice(possiblement)
            best_piece = index[0]
            best_mov = index[1]
            print(best_piece.piece_type, " ", best_mov)

        best_piece.application_movement(QPointF(best_mov[0], best_mov[1]), self.items(QPointF(best_mov[0] + 10, best_mov[1] + 10))[0])

        if self.analog_clock2.check_mate():
            self.label.setText("Black wins")
            self.analog_clock2.is_running = False
        else:
            square = self.items(QPointF(self.black_king.x + 10, self.black_king.y + 10),
                                        Qt.IntersectsItemShape)[0]
            square.setBrush(QBrush(QColor(square.color)))
            self.analog_clock2.is_running = False
            self.current_player = "white"
            self.white_move = True
            self.black_clock = False
            self.analog_clock.is_running = True
            self.label.setText("White move")
        white_king = self.white_king
        if white_king.is_in_check(white_king.x, white_king.y):
            square = self.items(QPointF(white_king.x + 10, white_king.y + 10), Qt.IntersectsItemShape)[
                0]
            square.setBrush(QBrush(QColor("red")))
        else:
            square = self.items(QPointF(white_king.x + 10, white_king.y + 10), Qt.IntersectsItemShape)[
                0]
            square.setBrush(QBrush(QColor(square.color)))
