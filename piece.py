from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from chess_square import ChessSquare
from promotiondialog import PromotionDialog

class ChessPiece(QGraphicsPixmapItem):
    def __init__(self, x, y, size, color, player, piece_type, filename):
        super().__init__(parent=None)
        self.color = color
        self.player = player
        self.piece_type = piece_type
        self.setPixmap(QPixmap(filename).scaled(size, size))
        self.setPos(x, y)
        self.selected = False
        self.offset = QPointF(0, 0)
        self.square_size = size
        self.x = x
        self.y = y
        self.possible_moves = []
        self.current_square = None
        self.old_colors = []
        self.has_moved = False
        self.en_passant = False
        self.check_moves = []
        self.my_king_check = False

    def mousePressEvent(self, event):
        if self.scene().white_move or self.scene().black_move:
            if self.scene().current_player == self.color:
                if event.button() == Qt.LeftButton:
                    self.selected = True
                    self.setOpacity(0.5)
                    self.offset = event.pos()
                    self.setZValue(1)
                    self.possible_moves = self.moves_continue()
                    self.highlight_moves()
    def mouseMoveEvent(self, event):
        if self.selected:
            new_pos = event.scenePos() - self.offset
            self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
            if self.scene().current_player == self.color:
                if event.button() == Qt.LeftButton:
                    if not self.sceneBoundingRect().intersects(self.scene().sceneRect()):
                        self.selected = False
                        self.setOpacity(1.0)
                        self.setPos(self.x, self.y)
                        return

                    squares = [item for item in self.collidingItems() if isinstance(item, ChessSquare)]
                    if squares:
                        square = squares[0]
                    else:
                        self.selected = False
                        self.setOpacity(1.0)
                        self.setPos(self.x, self.y)
                        return

                    new_pos = square.mapToScene(square.rect().center()) + QPointF(-40, -40)
                    if (new_pos.x(), new_pos.y()) in self.possible_moves:
                        self.application_movement(new_pos, square)
                    else:
                        self.setPos(self.x, self.y)

                    possible_moves = self.possible_moves
                    new_moves = [(move[0] + 10, move[1] + 10) for move in possible_moves]
                    squares = [square for move in new_moves for square in
                               self.scene().items(QPointF(*move), Qt.IntersectsItemShape) if
                               isinstance(square, ChessSquare)]

                    colors = self.old_colors[:len(squares)]
                    self.old_colors = self.old_colors[len(squares):]
                    list(map(lambda square, color: (
                        setattr(square, 'color', color), square.setBrush(QBrush(QColor(color)))), squares, colors))

                    self.selected = False
                    self.setOpacity(1.0)


    def application_movement(self, new_pos, square):
            self.current_square.piece = None
            self.current_square = square
            self.setPos(new_pos)
            self.setZValue(1)
            if self.piece_type == "king":
                if abs(self.x - new_pos.x()) > 90:
                    if new_pos.x() == 480:
                        square1 = self.scene().items(QPointF(570, new_pos.y() + 10), Qt.IntersectsItemShape)
                        piece1 = square1[0].piece
                        piece1.setPos(400, piece1.y)
                        piece1.x = 400
                        piece1.setZValue(1)
                        square1[0].piece = None
                        square2 = self.scene().items(QPointF(440, new_pos.y() + 10), Qt.IntersectsItemShape)
                        square2[0].piece = piece1
                        piece1.current_square = square2[0]
                    else:
                        square1 = self.scene().items(QPointF(0, new_pos.y() + 10), Qt.IntersectsItemShape)
                        piece1 = square1[0].piece
                        piece1.setPos(240, piece1.y)
                        piece1.x = 240
                        piece1.setZValue(1)
                        square1[0].piece = None
                        square2 = self.scene().items(QPointF(240, new_pos.y() + 10), Qt.IntersectsItemShape)
                        square2[0].piece = piece1
                        piece1.current_square = square2[0]
            if self.piece_type == "pawn":
                if abs(new_pos.y() - self.y) > 90:
                    self.en_passant = True
                else:
                    self.en_passant = False
                if abs(new_pos.x() - self.x) > 60:
                    if not self.is_square_occupied_TF(new_pos.x(), new_pos.y()):
                        if self.color == "white":
                            square1 = self.scene().items(QPointF(new_pos.x() + 10, new_pos.y() + 90),
                                                         Qt.IntersectsItemShape)
                            self.scene().white_pieces.remove(square1[0].piece)
                            self.scene().removeItem(square1[0].piece)
                            square1[0].piece = None
                        else:
                            square1 = self.scene().items(QPointF(new_pos.x() + 10, new_pos.y() - 60),
                                                         Qt.IntersectsItemShape)
                            self.scene().white_pieces.remove(square1[0].piece)
                            self.scene().removeItem(square1[0].piece)
                            square1[0].piece = None
                if new_pos.y() == 0 or new_pos.y() == 560:
                    self.pop_up_window()

            self.x = new_pos.x()
            self.y = new_pos.y()
            if square.piece is not None:
                self.scene().white_pieces.remove(square.piece)
                self.scene().removeItem(square.piece)

            square.piece = self
            self.has_moved = True
            if self.scene().white_move:
                self.scene().white_move = False
                self.scene().white_clock = True
            else:
                self.scene().black_move = False
                self.scene().black_clock = True



    def pop_up_window(self):
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        dialog = PromotionDialog()
        if dialog.exec_():
            selected_piece = dialog.get_selected_piece()
            if self.color == "white":
                if selected_piece == "queen":
                    self.piece_type = selected_piece
                    self.setPixmap(QPixmap(":/chess_pieces/icons/white_queen.png").scaled(self.square_size, self.square_size))
                elif selected_piece == "bishop":
                    self.piece_type = selected_piece
                    self.setPixmap(QPixmap(":/chess_pieces/icons/white_bishop.png").scaled(self.square_size, self.square_size))
                elif selected_piece == "rook":
                    self.piece_type = selected_piece
                    self.setPixmap(QPixmap(":/chess_pieces/icons/white_rook.png").scaled(self.square_size, self.square_size))
                else:
                    self.piece_type = selected_piece
                    self.setPixmap(QPixmap(":/chess_pieces/icons/white_knight.png").scaled(self.square_size, self.square_size))
            else:
                if selected_piece == "queen":
                    self.piece_type = selected_piece
                    self.setPixmap(QPixmap(":/chess_pieces/icons/black_queen.png").scaled(self.square_size, self.square_size))
                elif selected_piece == "bishop":
                    self.piece_type = selected_piece
                    self.setPixmap(QPixmap(":/chess_pieces/icons/black_bishop.png").scaled(self.square_size, self.square_size))
                elif selected_piece == "rook":
                    self.piece_type = selected_piece
                    self.setPixmap(QPixmap(":/chess_pieces/icons/black_rook.png").scaled(self.square_size, self.square_size))
                else:
                    self.piece_type = selected_piece
                    self.setPixmap(QPixmap(":/chess_pieces/icons/black_knight.png").scaled(self.square_size, self.square_size))

    def get_possible_moves(self, x, y):
        moves = []

        if self.piece_type == "pawn":
            if self.color == "white":
                square2 = self.scene().items(QPointF(x + 10, y + 10))[0]
                row = square2.row
                if row == 6:
                    two_squares_forward = (x, y - 2*self.square_size)
                    if not self.is_square_occupied_TF(*two_squares_forward):
                        if not self.is_square_occupied_TF(x, y - self.square_size):
                            moves.append(two_squares_forward)
                one_square_forward = (x, y - self.square_size)
                if not self.is_square_occupied_TF(*one_square_forward):
                    moves.append(one_square_forward)
                if square2.col != 0:
                    if self.is_square_occupied_TF(x - 80, y):
                        if self.is_square_occupied_C(x - 80, y) is not square2.piece.color:
                            square1 = self.scene().items(QPointF(x - 80, y), Qt.IntersectsItemShape)
                            piece1 = square1[0].piece
                            if piece1.en_passant:
                                moves.append((x - 80, y - 80))
                    left_diagonal_square = (x - 80, y - self.square_size)
                    if self.is_square_occupied_TF(*left_diagonal_square):
                        if self.is_square_occupied_C(*left_diagonal_square) is not square2.piece.color:
                            moves.append(left_diagonal_square)

                if square2.col != 7:
                    if self.is_square_occupied_TF(x + 80, y):
                        if self.is_square_occupied_C(x + 80, y) is not square2.piece.color:
                            square1 = self.scene().items(QPointF(x + 80, y), Qt.IntersectsItemShape)
                            piece1 = square1[0].piece
                            if piece1.en_passant:
                                moves.append((x + 80, y - 80))
                    right_diagonal_square = (x + 80, y - self.square_size)
                    if self.is_square_occupied_C(*right_diagonal_square) is not None:
                        if self.is_square_occupied_C(*right_diagonal_square) is not square2.piece.color:
                            moves.append(right_diagonal_square)

            else:
                square2 = self.scene().items(QPointF(x + 10, y + 10))[0]
                row = square2.row
                if row == 1:
                    two_squares_forward = (x, y + 2 * self.square_size)
                    if not self.is_square_occupied_TF(*two_squares_forward):
                        if not self.is_square_occupied_C(x, y + self.square_size):
                            moves.append(two_squares_forward)
                one_square_forward = (x, y + self.square_size)
                if not self.is_square_occupied_TF(*one_square_forward):
                    moves.append(one_square_forward)
                if square2.col != 0:
                    if self.is_square_occupied_TF(x - 80, y):
                        if self.is_square_occupied_C(x - 80, y) is not square2.piece.color:
                            square1 = self.scene().items(QPointF(x - 80, y), Qt.IntersectsItemShape)
                            piece1 = square1[0].piece
                            if piece1.en_passant:
                                moves.append((x - 80, y + 80))
                    one_square = (x - 80, y + self.square_size)
                    if self.is_square_occupied_C(*one_square) is not None:
                        if self.is_square_occupied_C(*one_square) is not square2.piece.color:
                            moves.append(one_square)
                if square2.col != 7:
                    if self.is_square_occupied_TF(x + 80, y):
                        if self.is_square_occupied_C(x + 80, y) is not square2.piece.color:
                            square1 = self.scene().items(QPointF(x + 80, y), Qt.IntersectsItemShape)
                            piece1 = square1[0].piece
                            if piece1.en_passant:
                                moves.append((x + 80, y + 80))
                    right_diagonal_square = (x + 80, y + self.square_size)
                    if self.is_square_occupied_C(*right_diagonal_square) is not None:
                        if self.is_square_occupied_C(*right_diagonal_square) is not square2.piece.color:
                            moves.append(right_diagonal_square)

        if self.piece_type == "rook" or self.piece_type == "queen":
            col = self.current_square.col
            row = self.current_square.row
            for i in range(row - 1, -1, -1):
                if self.is_square_occupied_TF(x, i * 80):
                    if self.is_square_occupied_C(x, i * 80) is not self.color:
                        moves.append((x, i * self.square_size))
                    break
                moves.append((x, i * self.square_size))
            for i in range(row + 1, 8):
                if self.is_square_occupied_TF(x, i * 80):
                    if self.is_square_occupied_C(x, i * 80) is not self.color:
                        moves.append((x, i * self.square_size))
                    break
                moves.append((x, i * self.square_size))
            for i in range(col + 1, 8):
                if self.is_square_occupied_TF(i * 80, y):
                    if self.is_square_occupied_C(i * 80, y) is not self.color:
                        moves.append((i * self.square_size, y))
                    break
                moves.append((i * self.square_size, y))
            for i in range(col - 1, -1, -1):
                if self.is_square_occupied_TF(i * 80, y):
                    if self.is_square_occupied_C(i * 80, y) is not self.color:
                        moves.append((i * self.square_size, y))
                    break
                moves.append((i * self.square_size, y))

        if self.piece_type == "bishop" or self.piece_type == "queen":
            col = self.current_square.col
            row = self.current_square.row
            i = 1
            while col + i < 8 and row - i >= 0:
                if self.is_square_occupied_TF((col + i) * self.square_size, (row - i) * self.square_size):
                    if self.is_square_occupied_C((col + i) * self.square_size,
                                               (row - i) * self.square_size) is not self.color:
                        moves.append(((col + i) * self.square_size, (row - i) * self.square_size))
                    break
                moves.append(((col + i) * self.square_size, (row - i) * self.square_size))
                i += 1
            i = 1
            while col - i >= 0 and row - i >= 0:
                if self.is_square_occupied_TF((col - i) * self.square_size, (row - i) * self.square_size):
                    if self.is_square_occupied_C((col - i) * self.square_size, (row - i) * self.square_size) is not self.color:
                        moves.append(((col - i) * self.square_size, (row - i) * self.square_size))
                    break
                moves.append(((col - i) * self.square_size, (row - i) * self.square_size))
                i += 1
            i = 1
            while col + i < 8 and row + i < 8:
                if self.is_square_occupied_TF((col + i) * self.square_size, (row + i) * self.square_size):
                    if self.is_square_occupied_C((col + i) * self.square_size, (row + i) * self.square_size) is not self.color:
                        moves.append(((col + i) * self.square_size, (row + i) * self.square_size))
                    break
                moves.append(((col + i) * self.square_size, (row + i) * self.square_size))
                i += 1
            i = 1
            while col - i >= 0 and row + i < 8:
                if self.is_square_occupied_TF((col - i) * self.square_size, (row + i) * self.square_size):
                    if self.is_square_occupied_C((col - i) * self.square_size, (row + i) * self.square_size) is not self.color:
                        moves.append(((col - i) * self.square_size, (row + i) * self.square_size))
                    break
                moves.append(((col - i) * self.square_size, (row + i) * self.square_size))
                i += 1

        if self.piece_type == "knight":
            col = self.current_square.col
            row = self.current_square.row
            possible_moves = [(col + 1, row + 2), (col + 2, row + 1), (col + 2, row - 1), (col + 1, row - 2),
                              (col - 1, row - 2), (col - 2, row - 1), (col - 2, row + 1), (col - 1, row + 2)]
            for move in possible_moves:
                if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                    if self.is_square_occupied_TF(move[0] * self.square_size, move[1] * self.square_size):
                        if self.is_square_occupied_C(move[0] * self.square_size, move[1] * self.square_size) is not self.color:
                            moves.append((move[0] * self.square_size, move[1] * self.square_size))
                    else:
                        moves.append((move[0] * self.square_size, move[1] * self.square_size))

        if self.piece_type == "king":
            col = self.current_square.col
            row = self.current_square.row
            if row > 0:
                if not self.is_square_occupied_C(col * self.square_size, (row - 1) * self.square_size) \
                        or self.is_square_occupied_C(col * self.square_size, (row - 1) * self.square_size) != self.color:
                    moves.append((col * self.square_size, (row - 1) * self.square_size))
                if col > 0:
                    if not self.is_square_occupied_C((col - 1) * self.square_size, (row - 1) * self.square_size) \
                            or self.is_square_occupied_C((col - 1) * self.square_size, (row - 1) * self.square_size) != self.color:
                        moves.append(((col - 1) * self.square_size, (row - 1) * self.square_size))
                if col < 7:
                    if not self.is_square_occupied_C((col + 1) * self.square_size, (row - 1) * self.square_size) \
                            or self.is_square_occupied_C((col + 1) * self.square_size, (row - 1) * self.square_size) != self.color:
                        moves.append(((col + 1) * self.square_size, (row - 1) * self.square_size))
            if row < 7:
                if not self.is_square_occupied_C(col * self.square_size, (row + 1) * self.square_size) \
                        or self.is_square_occupied_C(col * self.square_size, (row + 1) * self.square_size) != self.color:
                    moves.append((col * self.square_size, (row + 1) * self.square_size))
                if col > 0:
                    if not self.is_square_occupied_C((col - 1) * self.square_size, (row + 1) * self.square_size) \
                            or self.is_square_occupied_C((col - 1) * self.square_size, (row + 1) * self.square_size) != self.color:
                        moves.append(((col - 1) * self.square_size, (row + 1) * self.square_size))
                if col < 7:
                    if not self.is_square_occupied_C((col + 1) * self.square_size, (row + 1) * self.square_size) \
                            or self.is_square_occupied_C((col + 1) * self.square_size, (row + 1) * self.square_size) != self.color:
                        moves.append(((col + 1) * self.square_size, (row + 1) * self.square_size))
            if col > 0:
                if not self.is_square_occupied_C((col - 1) * self.square_size, row * self.square_size) \
                        or self.is_square_occupied_C((col - 1) * self.square_size, row * self.square_size) != self.color:
                    moves.append(((col - 1) * self.square_size, row * self.square_size))
            if col < 7:
                if not self.is_square_occupied_C((col + 1) * self.square_size, row * self.square_size) \
                        or self.is_square_occupied_C((col + 1) * self.square_size, row * self.square_size) != self.color:
                    moves.append(((col + 1) * self.square_size, row * self.square_size))
            if self.color == "white":
                items = self.scene().items(QPointF(570, 570))
                piece = items[0].piece
                if piece is not None and self.is_castling_allowed(piece):
                    moves.append((col * self.square_size + 160, row * self.square_size))
                items2 = self.scene().items(QPointF(10, 570))
                piece2 = items2[0].piece
                if piece2 is not None and self.is_castling_allowed(piece2):
                    moves.append((col * self.square_size - 160, row * self.square_size))
            else:
                items = self.scene().items(QPointF(570, 10))
                piece = items[0].piece
                if piece is not None and self.is_castling_allowed(piece):
                    moves.append((col * self.square_size + 160, row * self.square_size))
                items2 = self.scene().items(QPointF(10, 10))
                piece2 = items2[0].piece
                if piece2 is not None and self.is_castling_allowed(piece2):
                    moves.append((col * self.square_size - 160, row * self.square_size))

        return moves

    def moves_continue(self):
        x = self.scenePos().x()
        y = self.scenePos().y()
        possible_moves = self.get_possible_moves(x, y)
        possible_moves = [mov for mov in possible_moves if self.is_square_occupied_PT(*mov) != "king"]
        for pieces in self.scene().white_pieces:
            if pieces.piece_type== "king" and pieces.color == self.color:
                if not self.is_in_check(pieces.x, pieces.y):
                    pieces.my_king_check = False
                    new_possible_moves = []
                    for move in possible_moves:
                        if self.piece_type == "pawn" and abs(move[0] - self.x) > 60 and not self.is_square_occupied_TF(move[0], move[1]):
                            if self.color == "white":
                                old_square = self.current_square
                                self.current_square.piece = None
                                new_move = (move[0] + 10, move[1] + 10)
                                squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)
                                self.current_square = squares[0]
                                squares[0].piece = self
                                square5 = self.scene().items(QPointF(move[0] + 10, move[1] + 90),
                                                             Qt.IntersectsItemShape)
                                remember = square5[0].piece
                                self.scene().white_pieces.remove(square5[0].piece)
                                square5[0].piece = None
                                if not self.is_in_check(pieces.x, pieces.y):
                                    new_possible_moves.append(move)
                                square5[0].piece = remember
                                self.scene().white_pieces.append(square5[0].piece)
                                self.current_square.piece = None
                                self.current_square = old_square
                                self.current_square.piece = self
                            else:
                                old_square = self.current_square
                                self.current_square.piece = None
                                new_move = (move[0] + 10, move[1] + 10)
                                squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)
                                self.current_square = squares[0]
                                squares[0].piece = self
                                square5 = self.scene().items(QPointF(move[0] + 10, move[1] - 60),
                                                             Qt.IntersectsItemShape)
                                remember = square5[0].piece
                                self.scene().white_pieces.remove(square5[0].piece)
                                square5[0].piece = None
                                if not self.is_in_check(pieces.x, pieces.y):
                                    new_possible_moves.append(move)
                                square5[0].piece = remember
                                self.scene().white_pieces.append(square5[0].piece)
                                self.current_square.piece = None
                                self.current_square = old_square
                                self.current_square.piece = self
                        else:
                            old_square = self.current_square
                            self.current_square.piece = None
                            new_move = (move[0] + 10, move[1] + 10)
                            squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)
                            remember_new_square = squares[0].piece
                            self.current_square = squares[0]
                            if remember_new_square is not None:
                                self.scene().white_pieces.remove(squares[0].piece)
                            squares[0].piece = self
                            if self.piece_type != "king":
                                if not self.is_in_check(pieces.x, pieces.y):
                                    new_possible_moves.append(move)
                            else:
                                if not self.is_in_check(move[0], move[1]):
                                    new_possible_moves.append(move)
                            self.current_square.piece = None
                            self.current_square = old_square
                            self.current_square.piece = self
                            squares[0].piece = remember_new_square
                            if squares[0].piece is not None:
                                self.scene().white_pieces.append(squares[0].piece)
                    possible_moves = new_possible_moves
                else:
                    pieces.my_king_check = True
                    new_possible_moves = []
                    for move in possible_moves:
                        if self.piece_type == "pawn" and abs(move[0] - self.x) > 60 and not self.is_square_occupied_TF(move[0], move[1]):
                            if self.color == "white":
                                old_square = self.current_square
                                self.current_square.piece = None
                                new_move = (move[0] + 10, move[1] + 10)
                                squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)
                                self.current_square = squares[0]
                                squares[0].piece = self
                                square5 = self.scene().items(QPointF(move[0] + 10, move[1] + 90),
                                                             Qt.IntersectsItemShape)
                                remember = square5[0].piece
                                self.scene().white_pieces.remove(square5[0].piece)
                                square5[0].piece = None
                                if not self.is_in_check(pieces.x, pieces.y):
                                    new_possible_moves.append(move)
                                square5[0].piece = remember
                                self.scene().white_pieces.append(square5[0].piece)
                                self.current_square.piece = None
                                self.current_square = old_square
                                self.current_square.piece = self
                            else:
                                old_square = self.current_square
                                self.current_square.piece = None
                                new_move = (move[0] + 10, move[1] + 10)
                                squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)
                                self.current_square = squares[0]
                                squares[0].piece = self
                                square5 = self.scene().items(QPointF(move[0] + 10, move[1] - 60),
                                                             Qt.IntersectsItemShape)
                                remember = square5[0].piece
                                self.scene().white_pieces.remove(square5[0].piece)
                                square5[0].piece = None
                                if not self.is_in_check(pieces.x, pieces.y):
                                    new_possible_moves.append(move)
                                square5[0].piece = remember
                                self.scene().white_pieces.append(square5[0].piece)
                                self.current_square.piece = None
                                self.current_square = old_square
                                self.current_square.piece = self
                        else:
                            old_square = self.current_square
                            self.current_square.piece = None
                            new_move = (move[0] + 10, move[1] + 10)
                            squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)
                            remember_new_square = squares[0].piece
                            self.current_square = squares[0]
                            if squares[0].piece is not None:
                                self.scene().white_pieces.remove(squares[0].piece)
                            squares[0].piece = self

                            if self.piece_type != "king":
                                if not self.is_in_check(pieces.x, pieces.y):
                                    new_possible_moves.append(move)
                            else:
                                if not self.is_in_check(move[0], move[1]):
                                    new_possible_moves.append(move)
                            self.current_square.piece = None
                            self.current_square = old_square
                            self.current_square.piece = self
                            squares[0].piece = remember_new_square
                            if squares[0].piece is not None:
                                self.scene().white_pieces.append(squares[0].piece)
                    possible_moves = new_possible_moves
        return possible_moves

    def is_in_check(self, x, y):
        for pieces in self.scene().white_pieces:
            if pieces.color != self.color:
                if (x, y) in pieces.get_possible_moves(pieces.x, pieces.y):
                    return True
        return False

    def is_castling_allowed(self, rook):
        if self.has_moved or rook.has_moved:
            return False
        x1, y1 = self.x,  self.y
        x2, y2 = rook.x, rook.y
        if x1 < x2:
            if any(self.is_square_occupied_TF(x, y) for x, y in [(x1 + 80, y1), (x1 + 160, y1)]):
                return False
        else:
            if any(self.is_square_occupied_TF(x, y) for x, y in [(x1 - 80, y1), (x1 - 160, y1), (x1 - 240, y1)]):
                return False
        if self.my_king_check:
            return False
        return True

    def highlight_moves(self):
        self.old_colors = []
        for move in self.possible_moves:
            new_move = (move[0] + 10, move[1] + 10 )
            squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)
            square = squares[0]
            self.old_colors.append(square.color)
            square.color = "light green"
            square.setBrush(QBrush(QColor(square.color)))

    def is_square_occupied_C(self, x, y):
        items = self.scene().items(QPointF(x+10, y+10))
        square = items[0]
        if square.piece is not None:
            return square.piece.color
        return None
    def is_square_occupied_TF(self, x, y):
        items = self.scene().items(QPointF(x + 10, y + 10))
        square = items[0]
        if square.piece is not None:
            return True
        return False
    def is_square_occupied_PT(self, x, y):
        items = self.scene().items(QPointF(x+10, y+10))
        square = items[0]
        if square.piece is not None:
            return square.piece.piece_type
        return None