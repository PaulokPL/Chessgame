from szachownica import ChessBoard
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class MainWindow(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QGraphicsView()
        self.board = ChessBoard()
        self.view.setScene(self.board)

        # Create the second view and set its scene
        self.second_view = QGraphicsView()
        self.second_scene = QGraphicsScene()
        self.second_view.setScene(self.second_scene)

        # Create a vertical layout and add the views to it
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.second_view)

        # Create a main widget, set the layout on it, and set the main widget as the central widget of the main window
        widget = QWidget()
        widget.setLayout(layout)
        # self.setCentralWidget(widget)

        # Set the size of the main window
        self.resize(800, 800)