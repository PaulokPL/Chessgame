from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from chess_square import ChessSquare



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


    def mousePressEvent(self, event):
        # Sprawdza, czy pionek został kliknięty przez gracza
        if event.button() == Qt.LeftButton:
            # Jeśli tak, to ustawia jego stan jako "wybrany"
            # if self.scene().current_player == self.color:
                self.selected = True
                self.setOpacity(0.5)
                # Oblicza różnicę między pozycją myszy a pozycją pionka
                self.offset = event.pos()
                self.setZValue(1)
                self.possible_moves = self.get_possible_moves()
                # print(self.possible_moves)
                # if self.player == self.scene().current_player:
                self.highlight_moves()


    def mouseMoveEvent(self, event):
        # Sprawdza, czy pionek jest wybrany i przesuwa go na nową pozycję
        if self.selected:
            new_pos = event.scenePos() - self.offset
            # if new_pos.x() < 0 or new_pos.y() < 0 or new_pos.x() + self.square_size > self.scene().width() or new_pos.y() + self.square_size > self.scene().height():
            #     return
            self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Sprawdza, czy pionek został przeciągnięty poza planszę
            if self.sceneBoundingRect().intersects(self.scene().sceneRect()) == False:
                self.selected = False
                self.setOpacity(1.0)
                self.setPos(self.x, self.y)
                return
            # Znajduje pole na planszy, w którym pionek powinien zostać umieszczony
            for item in self.collidingItems():
                if isinstance(item, ChessSquare):
                    square = item
                    break
            else:
                # Pionek nie został przeciągnięty na żadne pole - resetuje stan
                self.selected = False
                self.setOpacity(1.0)
                self.setPos(self.x, self.y)
                return
            # Ustawia pozycję pionka na środek znalezionego pola
            new_pos = square.mapToScene(square.rect().center()) + QPointF(-40, -40)

            if (new_pos.x(), new_pos.y()) in self.possible_moves:
                # Ustawia pozycję pionka na środek znalezionego pola
                self.current_square.piece = None
                self.current_square = square
                self.setPos(new_pos)
                self.x = new_pos.x()
                self.y = new_pos.y()
                # Zapisuje referencję do pola, na którym się znajduje
                self.scene().removeItem(square.piece)
                square.piece = self
                # self.change_player()
            else:
                self.setPos(self.x, self.y)
                # square.piece = self
            for move in self.possible_moves:
                new_move = (move[0] + 10, move[1] + 10)
                squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)
                for square in squares:
                    if isinstance(square, ChessSquare):
                        color = self.old_colors.pop(0)
                        square.color = color
                        square.setBrush(QBrush(QColor(color)))

            # Resetuje stan
            self.selected = False
            self.setOpacity(1.0)
    def get_possible_moves(self):
        x = self.scenePos().x()
        y = self.scenePos().y()
        moves = []
        if self.piece_type == "pawn":
            if self.color == "white":
                # pionek biały, może przesunąć się o jedno pole do przodu
                square = self.collidingItems()[0]
                row = square.row
                if row == 6:
                    two_squares_forward = (x, y - 2*self.square_size)
                    if self.is_square_occupied(*two_squares_forward) is None and self.is_square_occupied(x, y - self.square_size) is None:
                        moves.append(two_squares_forward)
                    # to pierwszy ruch pionka, może przesunąć się o dwa pola do przodu
                one_square_forward = (x, y - self.square_size)
                if self.is_square_occupied(*one_square_forward) is None:
                    moves.append(one_square_forward)
                if square.col != 0:
                    left_diagonal_square = (x - 80, y - self.square_size)
                    if self.is_square_occupied(*left_diagonal_square) is not None and self.is_square_occupied(*left_diagonal_square) is not square.piece.color:
                        if self.is_square_occupiedv3(*left_diagonal_square) == 'king':
                            pass
                        else:
                            moves.append(left_diagonal_square)

                if square.col != 7:
                    right_diagonal_square = (x + 80, y - self.square_size)
                    if self.is_square_occupied(*right_diagonal_square) is not None and self.is_square_occupied(*right_diagonal_square) is not square.piece.color:
                        moves.append(right_diagonal_square)
            else:
                # pionek biały, może przesunąć się o jedno pole do przodu
                square = self.collidingItems()[0]
                row = square.row
                if row == 1:
                    two_squares_forward = (x, y + 2 * self.square_size)
                    if self.is_square_occupied(*two_squares_forward) is None and self.is_square_occupied(x, y + self.square_size) is None:
                        moves.append(two_squares_forward)
                    # to pierwszy ruch pionka, może przesunąć się o dwa pola do przodu
                one_square_forward = (x, y + self.square_size)
                if self.is_square_occupied(*one_square_forward) is None:
                    moves.append(one_square_forward)
                if square.col != 0:
                    one_square = (x - 80, y + self.square_size)
                    if self.is_square_occupied(*one_square) is not None and self.is_square_occupied(
                            *one_square) is not square.piece.color:
                        moves.append(one_square)
                if square.col != 7:
                    right_diagonal_square = (x + 80, y + self.square_size)
                    if self.is_square_occupied(*right_diagonal_square) is not None and self.is_square_occupied(
                            *right_diagonal_square) is not square.piece.color:
                        moves.append(right_diagonal_square)
        if self.piece_type == "rook" or self.piece_type == "queen":
            col = self.current_square.col
            row = self.current_square.row
            # ruchy do przodu
            for i in range(row - 1, -1, -1):
                if self.is_square_occupiedv2(x, i * 80):
                    if self.is_square_occupied(x, i * 80) is not self.color:
                        moves.append((x, i * self.square_size))
                    break
                moves.append((x, i * self.square_size))
            # ruchy do tyłu
            for i in range(row + 1, 8):
                if self.is_square_occupiedv2(x, i * 80):
                    if self.is_square_occupied(x, i * 80) is not self.color:
                        moves.append((x, i * self.square_size))
                    break
                moves.append((x, i * self.square_size))
            # ruchy w prawo
            for i in range(col + 1, 8):
                if self.is_square_occupiedv2(i * 80, y):
                    if self.is_square_occupied(i * 80, y) is not self.color:
                        moves.append((i * self.square_size, y))
                    break
                moves.append((i * self.square_size, y))
            # ruchy w lewo
            for i in range(col - 1, -1, -1):
                if self.is_square_occupiedv2(i * 80, y):
                    if self.is_square_occupied(i * 80, y) is not self.color:
                        moves.append((i * self.square_size, y))
                    break
                moves.append((i * self.square_size, y))
        if self.piece_type == "bishop" or self.piece_type == "queen":
            col = self.current_square.col
            row = self.current_square.row
            # ruchy w prawo i do góry
            i = 1
            while col + i < 8 and row - i >= 0:
                if self.is_square_occupiedv2((col + i) * self.square_size, (row - i) * self.square_size):
                    if self.is_square_occupied((col + i) * self.square_size,
                                               (row - i) * self.square_size) is not self.color:
                        moves.append(((col + i) * self.square_size, (row - i) * self.square_size))
                    break
                moves.append(((col + i) * self.square_size, (row - i) * self.square_size))
                i += 1
            # ruchy w lewo i do góry
            i = 1
            while col - i >= 0 and row - i >= 0:
                if self.is_square_occupiedv2((col - i) * self.square_size, (row - i) * self.square_size):
                    if self.is_square_occupied((col - i) * self.square_size, (row - i) * self.square_size) is not self.color:
                        moves.append(((col - i) * self.square_size, (row - i) * self.square_size))
                    break
                moves.append(((col - i) * self.square_size, (row - i) * self.square_size))
                i += 1

            # ruchy w prawo i do dołu
            i = 1
            while col + i < 8 and row + i < 8:
                if self.is_square_occupiedv2((col + i) * self.square_size, (row + i) * self.square_size):
                    if self.is_square_occupied((col + i) * self.square_size, (row + i) * self.square_size) is not self.color:
                        moves.append(((col + i) * self.square_size, (row + i) * self.square_size))
                    break
                moves.append(((col + i) * self.square_size, (row + i) * self.square_size))
                i += 1

            # ruchy w lewo i do dołu
            i = 1
            while col - i >= 0 and row + i < 8:
                if self.is_square_occupiedv2((col - i) * self.square_size, (row + i) * self.square_size):
                    if self.is_square_occupied((col - i) * self.square_size, (row + i) * self.square_size) is not self.color:
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
                    if self.is_square_occupiedv2(move[0] * self.square_size, move[1] * self.square_size):
                        if self.is_square_occupied(move[0] * self.square_size, move[1] * self.square_size) is not self.color:
                            moves.append((move[0] * self.square_size, move[1] * self.square_size))
                    else:
                        moves.append((move[0] * self.square_size, move[1] * self.square_size))
        if self.piece_type == "king":
            col = self.current_square.col
            row = self.current_square.row
            # ruchy do przodu
            if row > 0:
                if not self.is_square_occupied(col * self.square_size, (row - 1) * self.square_size) \
                        or self.is_square_occupied(col * self.square_size, (row - 1) * self.square_size) != self.color:
                    moves.append((col * self.square_size, (row - 1) * self.square_size))
                # ruchy na ukos w górę
                if col > 0:
                    if not self.is_square_occupied((col - 1) * self.square_size, (row - 1) * self.square_size) \
                            or self.is_square_occupied((col - 1) * self.square_size, (row - 1) * self.square_size) != self.color:
                        moves.append(((col - 1) * self.square_size, (row - 1) * self.square_size))
                if col < 7:
                    if not self.is_square_occupied((col + 1) * self.square_size, (row - 1) * self.square_size) \
                            or self.is_square_occupied((col + 1) * self.square_size, (row - 1) * self.square_size) != self.color:
                        moves.append(((col + 1) * self.square_size, (row - 1) * self.square_size))
            # ruchy w dół
            if row < 7:
                if not self.is_square_occupied(col * self.square_size, (row + 1) * self.square_size) \
                        or self.is_square_occupied(col * self.square_size, (row + 1) * self.square_size) != self.color:
                    moves.append((col * self.square_size, (row + 1) * self.square_size))
                # ruchy na ukos w dół
                if col > 0:
                    if not self.is_square_occupied((col - 1) * self.square_size, (row + 1) * self.square_size) \
                            or self.is_square_occupied((col - 1) * self.square_size, (row + 1) * self.square_size) != self.color:
                        moves.append(((col - 1) * self.square_size, (row + 1) * self.square_size))
                if col < 7:
                    if not self.is_square_occupied((col + 1) * self.square_size, (row + 1) * self.square_size) \
                            or self.is_square_occupied((col + 1) * self.square_size, (row + 1) * self.square_size) != self.color:
                        moves.append(((col + 1) * self.square_size, (row + 1) * self.square_size))
                # ruchy na boki
            if col > 0:
                if not self.is_square_occupied((col - 1) * self.square_size, row * self.square_size) \
                        or self.is_square_occupied((col - 1) * self.square_size, row * self.square_size) != self.color:
                    moves.append(((col - 1) * self.square_size, row * self.square_size))
            if col < 7:
                if not self.is_square_occupied((col + 1) * self.square_size, row * self.square_size) \
                        or self.is_square_occupied((col + 1) * self.square_size, row * self.square_size) != self.color:
                    moves.append(((col + 1) * self.square_size, row * self.square_size))
        for mov in moves:
            if self.is_square_occupiedv3(*mov) == "king":
                moves.remove(mov)
        return moves

    def highlight_moves(self):
        self.old_colors = []
        for move in self.possible_moves:
            new_move = (move[0] + 10, move[1] + 10 )
            squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)

            for square in squares:
                if isinstance(square, ChessSquare):
                    # zmień kolor pola, jeśli to możliwy ruch
                    self.old_colors.append(square.color)
                    square.color = "lightgreen"
                    square.setBrush(QBrush(QColor(square.color)))

    def is_square_occupied(self, x, y):
        items = self.scene().items(QPointF(x+10, y+10))
        for item in items:
            if isinstance(item, ChessSquare):
                square = item
                if square.piece is not None:
                    return square.piece.color
        return None

    def is_square_occupiedv2(self, x, y):
        items = self.scene().items(QPointF(x + 10, y + 10))
        for item in items:
            if isinstance(item, ChessSquare):
                square = item
                if square.piece != None:
                    return True
        return False
    def is_square_occupiedv3(self, x, y):
        items = self.scene().items(QPointF(x+10, y+10))
        for item in items:
            if isinstance(item, ChessSquare):
                square = item
                if square.piece is not None:
                    return square.piece.piece_type
        return None

    def change_player(self):
        if self.scene().current_player == "white":
            self.scene().current_player = "black"
        else:
            self.scene().current_player = "white"