import sys
import os
import requests
from PyQt5 import uic   # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from geocoder import get_coordinates, get_ll_span


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.map_ll = 19.894477, 54.643775
        self.map_l = 'map'
        self.map_zoom = 0.18712350000000022, 0.1377980000000001
        self.address_button.clicked.connect(self.show_map)
        self.show_map()

    def keyPressEvent(self, event) -> None:
        pass

    def refresh_map(self, event=None):
        map_params = {
            "ll": self.map_ll,
            "l": self.map_l,
            'spn': self.map_zoom
        }
        print(map_params)
        session = requests.Session()
        retry = Retry(total=10, connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get('https://static-maps.yandex.ru/1.x/',
                               params=map_params)
        print(response)
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')
        self.g_map.setPixmap(pixmap)
        os.remove('tmp.png')

    def show_map(self):
        address = self.address.text() if self.address.text() else 'Балтийск'
        self.map_ll, self.map_zoom = get_ll_span(address)
        self.refresh_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
