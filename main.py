from chess_board import ChessBoard
from PySide2.QtWidgets import *
from change_color import ChessBoardContextMenu
import chess_pieces_rc
from config_ip import ConfigDialogIP
if __name__ == '__main__':
    app = QApplication([])

    # utwórz dialog konfiguracyjny
    config_dialog = ConfigDialogIP()
    config_dialog.exec_()

    board = ChessBoard(config_dialog.game_mode, config_dialog.ip, config_dialog.port)
    view = ChessBoardContextMenu(board)
    view.setScene(board)
    view.show()
    view.setWindowTitle("Chess")
    view.setGeometry(100, 100, 1200, 900)

    app.exec_()