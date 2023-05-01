from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from math import sin, cos, pi

class AnalogClock(QGraphicsWidget):
    def __init__(self, clock, parent=None):
        super().__init__(parent)
        self.current_time = clock
        self.is_running = False

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        side = 200
        center = QPoint(100, 100)

        outer_radius = side / 2
        inner_radius = outer_radius * 0.9
        clock_face = QBrush(QColor(255, 255, 255))
        painter.setBrush(clock_face)
        painter.drawEllipse(center, outer_radius, outer_radius)
        painter.setBrush(Qt.black)
        painter.drawEllipse(center, 2, 2)

        minute_pen = QPen(QColor(0, 0, 0))
        minute_pen.setWidth(2)
        painter.setPen(minute_pen)
        minute_length = inner_radius
        for i in range(60):
            angle = i * 6
            x1 = center.x() + minute_length * sin(angle * pi / 180)
            y1 = center.y() + minute_length * cos(angle * pi / 180)
            x2 = center.x() + inner_radius * 0.9 * sin(angle * pi / 180)
            y2 = center.y() + inner_radius * 0.9 * cos(angle * pi / 180)
            painter.drawLine(QPointF(x2, y2), QPointF(x1, y1))

        minute_pen.setWidth(4)
        minute_pen.setColor(QColor(0, 0, 0))
        painter.setPen(minute_pen)
        minute_length = inner_radius * 0.7
        minute_angle = 6 * self.current_time.minute() + self.current_time.second() / 10
        x = center.x() + minute_length * sin(minute_angle * pi / 180)
        y = center.y() - minute_length * cos(minute_angle * pi / 180)
        painter.drawLine(center, QPointF(x, y))

        second_pen = QPen(QColor(0, 0, 255))
        painter.setPen(second_pen)
        second_length = inner_radius * 0.9
        second_angle = 6 * self.current_time.second() + self.current_time.msec() * 0.006
        x = center.x() + second_length * sin(second_angle * pi / 180)
        y = center.y() - second_length * cos(second_angle * pi / 180)
        painter.drawLine(center, QPointF(x, y))

        millisecond_pen = QPen(QColor(0, 255, 0))
        painter.setPen(millisecond_pen)
        millisecond_length = inner_radius * 0.8
        millisecond_angle = self.current_time.msec() / 1000 * 360
        x = center.x() + millisecond_length * sin(millisecond_angle * pi / 180)
        y = center.y() - millisecond_length * cos(millisecond_angle * pi / 180)
        painter.drawLine(center, QPointF(x, y))

    def update_time(self, time):
        if self.is_running:
            self.current_time = time
            self.update()

    def mousePressEvent(self, event):
        if self.is_running:
            if event.button() == Qt.LeftButton:
                if self.scene().white_clock and self.scene().analog_clock.is_running:
                    if self.scene().game_mode == "2 player":
                        self.scene().send_message()
                    if self.check_mate():
                        self.scene().label.setText("White wins")
                    else:
                        self.is_running = False
                        self.scene().current_player = "black"
                        self.scene().black_move = True
                        self.scene().white_clock = False
                        self.scene().analog_clock2.is_running = True
                        self.scene().label.setText("Black move")
                        square = self.scene().items(QPointF(self.scene().white_king.x + 10, self.scene().white_king.y + 10),Qt.IntersectsItemShape)[0]
                        square.setBrush(QBrush(QColor(square.color)))
                    black_king = self.scene().black_king
                    if black_king.is_in_check(black_king.x, black_king.y):
                        square = self.scene().items(QPointF(black_king.x + 10, black_king.y + 10), Qt.IntersectsItemShape)[0]
                        square.setBrush(QBrush(QColor("red")))
                    else:
                        square = self.scene().items(QPointF(black_king.x + 10, black_king.y + 10), Qt.IntersectsItemShape)[0]
                        square.setBrush(QBrush(QColor(square.color)))
                    if self.scene().game_mode == "AI":
                        self.scene().ai_movement()

                elif self.scene().black_clock and self.scene().current_player == "black":
                    if self.scene().game_mode == "2 player":
                        self.scene().send_message()
                    if self.scene().game_mode != "AI":
                        if self.check_mate():
                            self.scene().label.setText("Black wins")
                            self.is_running = False
                        else:
                            square = self.scene().items(QPointF(self.scene().black_king.x + 10, self.scene().black_king.y + 10), Qt.IntersectsItemShape)[0]
                            square.setBrush(QBrush(QColor(square.color)))
                            self.is_running = False
                            self.scene().current_player = "white"
                            self.scene().white_move = True
                            self.scene().black_clock = False
                            self.scene().analog_clock.is_running = True
                            self.scene().label.setText("White move")
                        white_king = self.scene().white_king
                        if white_king.is_in_check(white_king.x, white_king.y):
                            square = self.scene().items(QPointF(white_king.x + 10, white_king.y + 10), Qt.IntersectsItemShape)[0]
                            square.setBrush(QBrush(QColor("red")))
                        else:
                            square = self.scene().items(QPointF(white_king.x + 10, white_king.y + 10), Qt.IntersectsItemShape)[0]
                            square.setBrush(QBrush(QColor(square.color)))


    def check_mate(self):
        for pieces in self.scene().white_pieces:
            if pieces.color != self.scene().current_player:
                if len(pieces.moves_continue()) > 0:
                    return False
        return True