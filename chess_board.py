from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtGui import QPixmap
from PySide2.QtCore import QResource
from piece import ChessPiece
from chess_square import ChessSquare
from PySide2.QtWidgets import QGraphicsProxyWidget, QVBoxLayout, QPushButton

class ChessBoard(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(-50, -50, 800, 800)
        self.square_size = 80
        self.addRect(-80, -80, 800, 800, QPen(), QBrush(QColor("#c9b18b")))
        self.setBackgroundBrush(QBrush(QColor(162, 164, 168, 255)))
        self.white_pieces = []
        self.black_pieces = []
        self.current_player = "white"
        self.line_edit = QLineEdit()  # dodajemy pole QLineEdit
        self.line_edit.setGeometry(100, 721, 300, 30)
        self.button = QPushButton("Confirm")
        self.button.setGeometry(410, 721, 150, 30)
        self.button.clicked.connect(self.move_piece)
        # Create a QGraphicsProxyWidget and set its widget to the QLineEdit
        lineEdit_proxy = QGraphicsProxyWidget()
        lineEdit_proxy.setWidget(self.line_edit)
        self.addItem(lineEdit_proxy)
        button_proxy = QGraphicsProxyWidget()
        button_proxy.setWidget(self.button)
        self.addItem(button_proxy)
        self.addLabels()  # dodajemy etykiety do planszy
        QResource.registerResource("chess_pieces.qrc")

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
                    piece.current_square = square
                    square.piece = piece
                    self.addItem(piece)
                    if player == "white":
                        self.white_pieces.append(piece)
                    else:
                        self.black_pieces.append(piece)
                    # dodajemy element do tablicy
        # if self.board[0][0] is not None:
        #     print("Na pozycji (0, 0) znajduje się element")
    def changeBoardColor(self, color1, color2):
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

    def addLabels(self):
        # Dodajemy etykiety z literami od A do H
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

        # Dodajemy etykiety z numerami od 1 do 8
        for i in range(8):
            text = QGraphicsTextItem(str(i + 1))
            text.setFont(QFont("Arial", 16))
            text.setPos(-30, - i * 80 + 585 )
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
            piece.possible_moves = piece.get_possible_moves()
            if new_tuple_dst in piece.possible_moves:
                piece.apllication_movement(QPointF(*new_tuple_dst), dst_square[0])
        self.line_edit.clear()



    def parse_notation(self,notation):
        file_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        rank_map = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}

        # Ensure that the notation is in the correct format
        if len(notation) != 2:
            raise ValueError("Invalid notation: {}".format(notation))

        # Extract the file and rank from the notation
        file = notation[0]
        rank = notation[1]

        # Convert the file and rank to indices
        if file not in file_map or rank not in rank_map:
            raise ValueError("Invalid notation: {}".format(notation))
        x = file_map[file]
        y = rank_map[rank]

        return x, y