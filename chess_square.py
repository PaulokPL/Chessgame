from PySide2.QtGui import *
from PySide2.QtWidgets import *

class ChessSquare(QGraphicsRectItem):
    def __init__(self, x, y, size, color):
        super().__init__(x, y, size, size)
        self.color = color
        self.piece = None
        self.setBrush(QBrush(QColor(color)))
        self.x = x
        self.y = y
        self.row = int(self.y / size)
        self.col = int(self.x / size)