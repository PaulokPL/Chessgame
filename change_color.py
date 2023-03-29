from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class ChessBoardContextMenu(QGraphicsView):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pos):
        menu = QMenu()
        action = QAction("Change board color", self)
        action.triggered.connect(self.changeBoardColor)
        menu.addAction(action)
        menu.exec_(self.mapToGlobal(pos))

    def changeBoardColor(self):
        self.board.changeBoardColor("#779A58", "#EAEBC8")