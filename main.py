import sys
import os
import requests
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from geocoder import get_ll_span
from PyQt5 import QtCore, QtWidgets, QtGui


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.map_ll = 19.894477, 54.643775
        self.map_l = 'map'
        self.map_zoom = 10
        self.step = 0.01
        self.index_to_mapl = {0: 'map', 1: 'sat', 2: 'skl'}
        self.address_button.clicked.connect(self.show_map)
        self.minus_button.clicked.connect(self.zoom)
        self.plus_button.clicked.connect(self.zoom)
        self.mapl_combo.currentIndexChanged.connect(self.mapl_changed)
        self.show_map()

    def keyPressEvent(self, event) -> None:
        if event.key() == QtCore.Qt.Key_PageDown:
            self.zoom(key='-')
        if event.key() == QtCore.Qt.Key_PageUp:
            self.zoom(key='+')
        if event.key() == QtCore.Qt.Key_Up:
            self.change_coords('n')
        if event.key() == QtCore.Qt.Key_Down:
            self.change_coords('s')
        if event.key() == QtCore.Qt.Key_Left:
            self.change_coords('w')
        if event.key() == QtCore.Qt.Key_Right:
            self.change_coords('e')

    def refresh_map(self, event=None):
        map_params = {
            "ll": self.map_ll,
            "l": self.map_l,
            'z': self.map_zoom
        }
        session = requests.Session()
        retry = Retry(total=10, connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get('https://static-maps.yandex.ru/1.x/',
                               params=map_params)
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')
        self.g_map.setPixmap(pixmap)
        os.remove('tmp.png')

    def show_map(self):
        address = self.address.text() if self.address.text() else 'Балтийск'
        self.map_ll, _ = get_ll_span(address)
        self.refresh_map()

    def zoom(self, _=None, key=None):
        if key is None:
            key = self.sender().text()
        if key == '+':
            self.map_zoom = min(self.map_zoom + 1, 17)
            self.step = max(self.step - 0.1, 0.01)
        else:
            self.step = min(self.step + 0.1, 15)
            self.map_zoom = max(self.map_zoom - 1, 0)
        self.refresh_map()

    def mapl_changed(self, index):
        self.map_l = self.index_to_mapl[index]
        self.refresh_map()

    def change_coords(self, direction):
        l2, l1 = map(float, self.map_ll.split(','))
        match direction:
            case 'n':
                l1 = min(90, l1 + self.step)
            case 's':
                l1 = max(-90, l1 - self.step)
            case 'e':
                l2 = min(180, l2 + self.step)
            case 'w':
                l2 = max(-180, l2-self.step)
        self.map_ll = f'{l2},{l1}'
        self.refresh_map()




if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
