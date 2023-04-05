from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class ChessBoardContextMenu(QGraphicsView):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        menu = QMenu()
        action = QAction("Change board color", self)
        action.triggered.connect(self.change_board_color)
        menu.addAction(action)
        menu.exec_(self.mapToGlobal(pos))

    def change_board_color(self):
        self.board.change_board_color("#779A58", "#EAEBC8")