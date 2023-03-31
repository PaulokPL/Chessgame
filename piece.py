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
            # if new_pos.x() < -10 or new_pos.y() < -10 or new_pos.x() + self.square_size > self.scene().width() + 10 or new_pos.y() + self.square_size > self.scene().height() + 10:
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
                # Pionek nie został przeciągnięty na żadne pole-resetuje stan
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
                        if not self.is_square_occupiedv2(new_pos.x(), new_pos.y()):
                            if self.color == "white":
                                square1 = self.scene().items(QPointF(new_pos.x() + 10, new_pos.y() + 90), Qt.IntersectsItemShape)
                                self.scene().removeItem(square1[0].piece)
                                square1[0].piece = None
                            else:
                                square1 = self.scene().items(QPointF(new_pos.x() + 10, new_pos.y() - 60), Qt.IntersectsItemShape)
                                self.scene().removeItem(square1[0].piece)
                                square1[0].piece = None
                    if new_pos.y() == 0 or new_pos.y() == 560:
                        self.pop_up_window()

                self.x = new_pos.x()
                self.y = new_pos.y()
                # Zapisuje referencję do pola, na którym się znajduje
                self.scene().removeItem(square.piece)
                square.piece = self
                # self.change_player()
                self.has_moved = True
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
                self.setPixmap(
                    QPixmap(":/chess_pieces/icons/white_rook.png").scaled(self.square_size, self.square_size))
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

    def get_possible_moves(self):
        x = self.scenePos().x()
        y = self.scenePos().y()
        moves = []
        if self.piece_type == "pawn":
            if self.color == "white":
                # pionek biały może przesunąć się o jedno pole do przodu
                square = self.collidingItems()[0]
                row = square.row
                if row == 6:
                    two_squares_forward = (x, y - 2*self.square_size)
                    if self.is_square_occupied(*two_squares_forward) is None and self.is_square_occupied(x, y - self.square_size) is None:
                        moves.append(two_squares_forward)
                    # to pierwszy ruch pionka może przesunąć się o dwa pola do przodu
                one_square_forward = (x, y - self.square_size)
                if self.is_square_occupied(*one_square_forward) is None:
                    moves.append(one_square_forward)
                if square.col != 0:
                    if self.is_square_occupiedv2(x - 80, y) and self.is_square_occupied(x - 80, y) is not square.piece.color:
                        square1 = self.scene().items(QPointF(x - 80, y), Qt.IntersectsItemShape)
                        piece1 = square1[0].piece
                        if piece1.en_passant:
                            moves.append((x - 80, y - 80))
                    left_diagonal_square = (x - 80, y - self.square_size)
                    if self.is_square_occupied(*left_diagonal_square) is not None and self.is_square_occupied(*left_diagonal_square) is not square.piece.color:
                        if self.is_square_occupiedv3(*left_diagonal_square) == 'king':
                            pass
                        else:
                            moves.append(left_diagonal_square)

                if square.col != 7:
                    if self.is_square_occupiedv2(x + 80, y) and self.is_square_occupied(x + 80,
                                                                                        y) is not square.piece.color:
                        square1 = self.scene().items(QPointF(x + 80, y), Qt.IntersectsItemShape)
                        piece1 = square1[0].piece
                        if piece1.en_passant:
                            moves.append((x + 80, y - 80))
                    right_diagonal_square = (x + 80, y - self.square_size)
                    if self.is_square_occupied(*right_diagonal_square) is not None and self.is_square_occupied(*right_diagonal_square) is not square.piece.color:
                        moves.append(right_diagonal_square)


            else:
                # pionek biały może przesunąć się o jedno pole do przodu
                square = self.collidingItems()[0]
                row = square.row
                if row == 1:
                    two_squares_forward = (x, y + 2 * self.square_size)
                    if self.is_square_occupied(*two_squares_forward) is None and self.is_square_occupied(x, y + self.square_size) is None:
                        moves.append(two_squares_forward)
                    # to pierwszy ruch pionka może przesunąć się o dwa pola do przodu
                one_square_forward = (x, y + self.square_size)
                if self.is_square_occupied(*one_square_forward) is None:
                    moves.append(one_square_forward)
                if square.col != 0:
                    if self.is_square_occupiedv2(x - 80, y) and self.is_square_occupied(x - 80, y) is not square.piece.color:
                        square1 = self.scene().items(QPointF(x - 80, y), Qt.IntersectsItemShape)
                        piece1 = square1[0].piece
                        if piece1.en_passant:
                            moves.append((x - 80, y + 80))
                    one_square = (x - 80, y + self.square_size)
                    if self.is_square_occupied(*one_square) is not None and self.is_square_occupied(
                            *one_square) is not square.piece.color:
                        moves.append(one_square)
                if square.col != 7:
                    if self.is_square_occupiedv2(x + 80, y) and self.is_square_occupied(x + 80,
                                                                                        y) is not square.piece.color:
                        square1 = self.scene().items(QPointF(x + 80, y), Qt.IntersectsItemShape)
                        piece1 = square1[0].piece
                        if piece1.en_passant:
                            moves.append((x + 80, y + 80))
                    right_diagonal_square = (x + 80, y + self.square_size)
                    if self.is_square_occupied(*right_diagonal_square) is not None and \
                            self.is_square_occupied(*right_diagonal_square) is not square.piece.color:
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
            if self.color == "white":
                items = self.scene().items(QPointF(570, 570))
                for item in items:
                    if isinstance(item, ChessSquare):
                        piece = item.piece
                        if self.is_castling_allowed(piece):
                            moves.append((col * self.square_size + 160, row * self.square_size))
                items2 = self.scene().items(QPointF(10, 570))
                for item in items2:
                    if isinstance(item, ChessSquare):
                        piece = item.piece
                        if self.is_castling_allowed(piece):
                            moves.append((col * self.square_size - 160, row * self.square_size))
            else:
                items = self.scene().items(QPointF(570, 10))
                for item in items:
                    if isinstance(item, ChessSquare):
                        piece = item.piece
                        if self.is_castling_allowed(piece):
                            moves.append((col * self.square_size + 160, row * self.square_size))
                items2 = self.scene().items(QPointF(10, 10))
                for item in items2:
                    if isinstance(item, ChessSquare):
                        piece = item.piece
                        if self.is_castling_allowed(piece):
                            moves.append((col * self.square_size - 160, row * self.square_size))
                # if self.is_castling_allowed():
                #     moves.append()
        for mov in moves:
            if self.is_square_occupiedv3(*mov) == "king":
                moves.remove(mov)
        return moves

    def is_castling_allowed(self, rook):
        if self.has_moved or rook.has_moved:
            return False
        x1, y1 = self.scenePos().x(), self.scenePos().y()
        x2, y2 = rook.scenePos().x(), rook.scenePos().y()
        if x1 < x2:  # king side castling
            if any(self.is_square_occupiedv2(x, y) for x, y in [(x1 + 80, y1), (x1 + 160, y1)]):
                return False
        else:  # queen side castling
            if any(self.is_square_occupiedv2(x, y) for x, y in [(x1 - 80, y1), (x1 - 160, y1), (x1 - 240, y1)]):
                return False
        # # Check if the king is not in check and won't be in check after the move
        # if self.is_in_check() or self.is_in_check_after_move(x2, y2):
        #     return False
        return True
    def highlight_moves(self):
        self.old_colors = []
        for move in self.possible_moves:
            new_move = (move[0] + 10, move[1] + 10 )
            squares = self.scene().items(QPointF(*new_move), Qt.IntersectsItemShape)

            for square in squares:
                if isinstance(square, ChessSquare):
                    # zmień kolor pola, jeśli to możliwy ruch
                    self.old_colors.append(square.color)
                    square.color = "light green"
                    square.setBrush(QBrush(QColor(square.color)))

    def is_square_occupied(self, x, y):
        items = self.scene().items(QPointF(x+10, y+10))
        # for item in items:
        #     if isinstance(item, ChessSquare):
        square = items[0]
        if square.piece is not None:
            return square.piece.color
        return None

    def is_square_occupiedv1(self, x, y):
        items = self.scene().items(QPointF(x + 10, y + 10))
        # for item in items:
        #     if isinstance(item, ChessSquare):
        square = items[0]
        if square.piece is not None:
            return square.piece
        return None

    def is_square_occupiedv2(self, x, y):
        items = self.scene().items(QPointF(x + 10, y + 10))
        # for item in items:
        #     if isinstance(item, ChessSquare):
        square = items[0]
        if square.piece is not None:
            return True
        return False
    def is_square_occupiedv3(self, x, y):
        items = self.scene().items(QPointF(x+10, y+10))
        # for item in items:
        #     if isinstance(item, ChessSquare):
        square = items[0]
        if square.piece is not None:
            return square.piece.piece_type
        return None

    def change_player(self):
        if self.scene().current_player == "white":
            self.scene().current_player = "black"
        else:
            self.scene().current_player = "white"