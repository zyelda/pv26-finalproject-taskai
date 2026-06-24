import os
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def icon(name: str, color: str = None) -> QIcon:
    """Muat ikon dari assets/icons. Jika `color` diberikan, ikon (yang
    berupa siluet hitam) akan diwarnai ulang agar tetap terlihat di
    background gelap (mis. sidebar)."""
    path = os.path.join(_BASE, "assets", "icons", name)
    if color is None:
        return QIcon(path)

    src = QPixmap(path)
    tinted = QPixmap(src.size())
    tinted.fill(Qt.transparent)
    painter = QPainter(tinted)
    painter.drawPixmap(0, 0, src)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), QColor(color))
    painter.end()
    return QIcon(tinted)

def pixmap(name: str) -> QPixmap:
    return QPixmap(os.path.join(_BASE, "assets", "icons", name))