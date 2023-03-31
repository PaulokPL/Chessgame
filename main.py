from chess_board import ChessBoard
from PySide2.QtWidgets import *
from change_color import ChessBoardContextMenu
import chess_pieces_rc

if __name__ == '__main__':
    app = QApplication([])
    board = ChessBoard()
    view = ChessBoardContextMenu(board)
    view.setScene(board)
    view.show()
    view.setWindowTitle("Chess")
    view.setGeometry(100,100, 1200, 900)
    app.exec_()