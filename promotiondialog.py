from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide2 import QtCore

class PromotionDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.selected_piece = None
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()

        label = QLabel("Choose a piece to promote to:")
        vbox.addWidget(label)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # hbox = QHBoxLayout()

        queen_btn = QPushButton("Queen")
        queen_btn.clicked.connect(lambda: self.set_selected_piece("queen"))
        vbox.addWidget(queen_btn)

        rook_btn = QPushButton("Rook")
        rook_btn.clicked.connect(lambda: self.set_selected_piece("rook"))
        vbox.addWidget(rook_btn)

        bishop_btn = QPushButton("Bishop")
        bishop_btn.clicked.connect(lambda: self.set_selected_piece("bishop"))
        vbox.addWidget(bishop_btn)

        knight_btn = QPushButton("Knight")
        knight_btn.clicked.connect(lambda: self.set_selected_piece("knight"))
        vbox.addWidget(knight_btn)

        # vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle("Promotion Dialog")
        self.setModal(True)

    def set_selected_piece(self, piece):
        self.selected_piece = piece
        self.accept()

    def get_selected_piece(self):
        return self.selected_piece