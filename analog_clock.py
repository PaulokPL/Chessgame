from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
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

        # draw the clock face
        outer_radius = side / 2
        inner_radius = outer_radius * 0.9
        clock_face = QBrush(QColor(255, 255, 255))
        painter.setBrush(clock_face)
        painter.drawEllipse(center, outer_radius, outer_radius)
        painter.setBrush(Qt.black)
        painter.drawEllipse(center, 2, 2)


        # draw the minute marks
        minute_pen = QPen(QColor(0, 0, 0))
        minute_pen.setWidth(2)
        for i in range(60):
            angle = i * 6
            minute_length = inner_radius * 1
            x1 = center.x() + minute_length * sin(angle * pi / 180)
            y1 = center.y() + minute_length * cos(angle * pi / 180)
            x2 = center.x() + inner_radius * 0.9 * sin(angle * pi / 180)
            y2 = center.y() + inner_radius * 0.9 * cos(angle * pi / 180)
            painter.setPen(minute_pen)
            painter.drawLine(QPointF(x2, y2), QPointF(x1, y1))

        # draw the minute hand
        minute_pen.setWidth(4)
        minute_pen.setColor(QColor(0, 0, 0))
        painter.setPen(minute_pen)
        minute_length = inner_radius * 0.7
        minute_angle = 6 * self.current_time.minute() + self.current_time.second() / 10
        x = center.x() + minute_length * sin(minute_angle * pi / 180)
        y = center.y() - minute_length * cos(minute_angle * pi / 180)
        painter.drawLine(center, QPointF(x, y))

        # draw the second hand
        second_pen = QPen(QColor(0, 0, 255))
        painter.setPen(second_pen)
        second_length = inner_radius * 0.9
        second_angle = 6 * self.current_time.second() + self.current_time.msec() * 0.006
        x = center.x() + second_length * sin(second_angle * pi / 180)
        y = center.y() - second_length * cos(second_angle * pi / 180)
        painter.drawLine(center, QPointF(x, y))

        # draw the millisecond hand
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
                    self.is_running = False
                    self.scene().current_player = "black"
                    self.scene().black_move = True
                    self.scene().white_clock = False
                    self.scene().analog_clock2.is_running = True
                elif self.scene().black_clock and self.scene().current_player == "black":
                    self.is_running = False
                    self.scene().current_player = "white"
                    self.scene().white_move = True
                    self.scene().black_clock = False
                    self.scene().analog_clock.is_running = True