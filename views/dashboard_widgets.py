from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget


class MetricCard(QWidget):
    def __init__(self, title: str, value: str, subtitle: str = ""):
        super().__init__()
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.setMinimumHeight(92)
        self.setStyleSheet(
            "QWidget { background: #ffffff; border: 1px solid #dbe3ea; "
            "border-radius: 8px; }"
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor("#172b3a"))
        painter.setFont(QFont("Segoe UI", 25, QFont.Bold))
        painter.drawText(16, 36, self.value)
        painter.setPen(QColor("#526474"))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(16, 58, self.title)
        if self.subtitle:
            painter.drawText(16, 76, self.subtitle)


class BarChart(QWidget):
    def __init__(self, title: str, values: dict[str, int]):
        super().__init__()
        self.title = title
        self.values = values
        self.setMinimumSize(430, 280)
        self.setStyleSheet("background: #ffffff; border: 1px solid #dbe3ea; border-radius: 8px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor("#172b3a"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.drawText(18, 28, self.title)
        if not self.values:
            return
        left, top, right, bottom = 48, 48, 18, 42
        chart = QRectF(left, top, self.width() - left - right, self.height() - top - bottom)
        maximum = max(self.values.values()) or 1
        bar_width = chart.width() / len(self.values) * 0.62
        gap = chart.width() / len(self.values)
        painter.setPen(QColor("#9aa9b5"))
        painter.drawLine(chart.left(), chart.bottom(), chart.right(), chart.bottom())
        painter.setFont(QFont("Segoe UI", 8))
        for index, (label, value) in enumerate(self.values.items()):
            height = (value / maximum) * (chart.height() - 12)
            x = chart.left() + index * gap + (gap - bar_width) / 2
            y = chart.bottom() - height
            painter.setBrush(QColor("#4d9bd3"))
            painter.setPen(Qt.NoPen)
            painter.drawRect(QRectF(x, y, bar_width, height))
            painter.setPen(QColor("#526474"))
            painter.drawText(QRectF(x - 8, y - 18, bar_width + 16, 16), Qt.AlignCenter, str(value))
            painter.drawText(QRectF(x - 18, chart.bottom() + 8, bar_width + 36, 28), Qt.AlignCenter | Qt.TextWordWrap, label)


class PieChart(QWidget):
    def __init__(self, title: str, values: dict[str, int]):
        super().__init__()
        self.title = title
        self.values = values
        self.setMinimumSize(330, 280)
        self.setStyleSheet("background: #ffffff; border: 1px solid #dbe3ea; border-radius: 8px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor("#172b3a"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.drawText(18, 28, self.title)
        total = sum(self.values.values())
        if not total:
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(20, 150, "Sem dados")
            return
        diameter = min(self.height() - 82, 170)
        rect = QRectF(22, 52, diameter, diameter)
        colors = [QColor("#4d9bd3"), QColor("#f2ae24"), QColor("#68b984"), QColor("#d66b6b")]
        start = 0
        painter.setPen(Qt.NoPen)
        for index, (label, value) in enumerate(self.values.items()):
            span = round(value / total * 360 * 16)
            painter.setBrush(colors[index % len(colors)])
            painter.drawPie(rect, start, span)
            start += span
        painter.setFont(QFont("Segoe UI", 9))
        legend_x = diameter + 42
        for index, (label, value) in enumerate(self.values.items()):
            y = 82 + index * 28
            painter.setBrush(colors[index % len(colors)])
            painter.drawEllipse(QRectF(legend_x, y - 8, 10, 10))
            painter.setPen(QColor("#526474"))
            percentage = value / total * 100
            painter.drawText(legend_x + 17, y, f"{label}: {value} ({percentage:.1f}%)")


class Gauge(QWidget):
    def __init__(self, title: str, value: float, maximum: float, display: str):
        super().__init__()
        self.title = title
        self.value = max(0, value)
        self.maximum = max(1, maximum)
        self.display = display
        self.setMinimumSize(240, 180)
        self.setStyleSheet("background: #ffffff; border: 1px solid #dbe3ea; border-radius: 8px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor("#172b3a"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
        painter.drawText(14, 25, self.title)
        diameter = min(self.width() - 56, self.height() - 74)
        rect = QRectF((self.width() - diameter) / 2, 42, diameter, diameter)
        pen = QPen(QColor("#e5ebf0"), 18, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 180 * 16, -180 * 16)
        ratio = min(self.value / self.maximum, 1)
        pen.setColor(QColor("#4d9bd3"))
        painter.setPen(pen)
        painter.drawArc(rect, 180 * 16, int(-180 * 16 * ratio))
        painter.setPen(QColor("#172b3a"))
        painter.setFont(QFont("Segoe UI", 19, QFont.Bold))
        painter.drawText(QRectF(0, self.height() - 54, self.width(), 30), Qt.AlignCenter, self.display)
