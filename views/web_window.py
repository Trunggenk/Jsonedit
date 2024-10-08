from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
import qtawesome as qta  # Import QtAwesome
import os

class WebWindow(QMainWindow):
    """Cửa sổ riêng hiển thị kết quả Google Search"""
    def __init__(self, url):
        super().__init__()

        self.setWindowTitle('Google Search')
        self.setGeometry(200, 200, 800, 600)  # Kích thước mặc định

        # Đường dẫn đến icon cửa sổ chính
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'resource', 'icon_google.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Khởi tạo QWebEngineView
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl(url))

        # Tạo thanh công cụ (Toolbar)
        self.toolbar = QToolBar("Navigation")
        self.addToolBar(self.toolbar)

        # Tạo nút "Back" với QtAwesome icon (ei.arrow-left)
        back_action = QAction(qta.icon('ei.arrow-left'), "Back", self)
        back_action.triggered.connect(self.go_back)
        self.toolbar.addAction(back_action)

        layout = QVBoxLayout()
        layout.addWidget(self.web_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def go_back(self):
        """Quay lại trang trước đó."""
        if self.web_view.history().canGoBack():
            self.web_view.back()
