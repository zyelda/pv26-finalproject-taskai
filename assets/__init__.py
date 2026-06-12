import os
from PySide6.QtGui import QIcon, QPixmap

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def icon(name: str) -> QIcon:
    return QIcon(os.path.join(_BASE, "assets", "icons", name))

def pixmap(name: str) -> QPixmap:
    return QPixmap(os.path.join(_BASE, "assets", "icons", name))