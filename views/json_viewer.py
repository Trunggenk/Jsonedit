from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QWidget, QFileDialog,
    QMessageBox, QLabel, QShortcut, QLineEdit, QTreeWidgetItem,QMenu
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QTransform, QColor, QDesktopServices, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QUrl
import os
import qtawesome as qta
from .file_loader import load_json_file
from .utils import parse_json_tree, tree_to_dict
from .web_window import WebWindow
import json
from datetime import datetime

class JSONViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'resource', 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.web_window_position = None
        self.web_window_size = None
        self.json_data = []
        self.original_data = []

        self.setWindowTitle('QT_JsonHandler')
        self.setGeometry(100, 100, 1000, 900)

        # Tạo layout chính
        self.main_layout = QVBoxLayout()

        # Tạo layout cho nút bấm và hình ảnh auto-save
        self.top_layout = QHBoxLayout()

        # Tạo nút "Load" và "Save"
        self.load_button = QPushButton("Load JSON File")
        self.load_button.clicked.connect(self.load_json_file)
        self.top_layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save JSON File")
        self.save_button.clicked.connect(self.save_json_file)
        self.top_layout.addWidget(self.save_button)

        # Thêm một nhãn (label) để hiển thị icon "Auto Save"
        self.auto_save_label = QLabel()
        self.auto_save_icon = qta.icon('mdi.autorenew', color='blue')
        self.auto_save_label.setPixmap(self.auto_save_icon.pixmap(64, 64))
        self.auto_save_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.top_layout.addWidget(self.auto_save_label)

        # Thêm layout của nút và hình ảnh vào layout chính
        self.main_layout.addLayout(self.top_layout)

        # Thêm search box
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search root by name...")
        self.search_box.returnPressed.connect(self.search_tree)
        self.main_layout.addWidget(self.search_box)

        # Tạo cây để hiển thị JSON
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        self.tree_widget.setColumnWidth(0, 250)
        self.tree_widget.setColumnWidth(1, 650)

        font = QFont()
        font.setPointSize(12)
        self.tree_widget.setFont(font)
        self.main_layout.addWidget(self.tree_widget)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        self.tree_widget.itemChanged.connect(self.on_item_changed)

        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        #
        self.rotation_angle = 0
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.rotate_icon)
        self.rotation_timer.start(60000)
        #
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)

    def search_tree(self):

        search_text = self.search_box.text().lower()

        if search_text:
            for i in range(self.tree_widget.topLevelItemCount()):
                root_item = self.tree_widget.topLevelItem(i)
                root_name = root_item.text(0).lower()

                if search_text in root_name:
                    self.tree_widget.setCurrentItem(root_item)
                    root_item.setExpanded(True)
                else:
                    root_item.setExpanded(False)

    def rotate_icon(self):
        self.rotation_angle = (self.rotation_angle + 30) % 360
        transform = QTransform().rotate(self.rotation_angle)
        rotated_pixmap = self.auto_save_icon.pixmap(64, 64).transformed(transform)
        self.auto_save_label.setPixmap(rotated_pixmap)

    def show_context_menu(self, position):
        item = self.tree_widget.itemAt(position)
        if item and not item.parent():  # Only show context menu for root items (no parent)
            menu = QMenu(self)
            delete_action = menu.addAction("Delete")
            action = menu.exec_(self.tree_widget.viewport().mapToGlobal(position))

            if action == delete_action:
                self.delete_root_item(item)

    def delete_root_item(self, item):
        # Confirm deletion
        confirm = QMessageBox.question(self, "Delete", f"Are you sure you want to delete '{item.text(0)}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            index = self.tree_widget.indexOfTopLevelItem(item)
            if index != -1:
                self.tree_widget.takeTopLevelItem(index)
                del self.json_data[index]

    def load_json_file(self):
        self.json_data= load_json_file(self)
        self.original_data = self.json_data.copy()
        if self.json_data:
            self.display_json_tree(self.json_data)

    def display_json_tree(self, json_data):
        self.tree_widget.clear()
        for restaurant in json_data:
            parse_json_tree(restaurant, self.tree_widget)

        self.add_url_click_action()



    def on_item_clicked(self, item, column):
        if item.childCount() > 0:
            if item.isExpanded():
                item.setExpanded(False)
            else:
                self.expand_all_children(item)


        if column == 0 and not item.parent():
            restaurant_name = item.text(0)
            self.open_web_window(restaurant_name)

    def open_web_window(self, restaurant_name):

        search_url = f"https://www.google.com/search?q={restaurant_name}"
        self.web_window = WebWindow(search_url)
        if self.web_window_position:
            self.web_window.move(self.web_window_position)
        else:

            self_position = self.geometry()
            new_x = self_position.x() + self_position.width() + 20
            new_y = self_position.y()
            self.web_window.move(new_x, new_y)
        if self.web_window_size:
            self.web_window.resize(self.web_window_size)
        else:
            self.web_window.resize(800, 600)

        self.web_window.show()
        self.web_window.moveEvent = self.update_web_window_position
        self.web_window.resizeEvent = self.update_web_window_size

    def update_web_window_position(self, event):

        if self.web_window:
            self.web_window_position = self.web_window.pos()  # Lưu vị trí mới

    def update_web_window_size(self, event):
        if self.web_window:
            self.web_window_size = self.web_window.size()

    def on_item_changed(self, item, column):

        if column == 1:  #
            item.setForeground(1, QColor("green"))
            if item.text(1) == "No value":
                item.setForeground(1, QColor("red"))
            else:
                item.setForeground(1, QColor("green"))
    def expand_all_children(self, item):
        item.setExpanded(True)
        for i in range(item.childCount()):
            child = item.child(i)
            self.expand_all_children(child)

    def on_item_double_clicked(self, item, column):
        if column == 1:
            key = item.text(0)
            if key != "name":
                self.tree_widget.editItem(item, column)

    def add_url_click_action(self):

        def open_url_on_click(item, column):
            # Kiểm tra nếu mục có tên 'post_url'
            if item.text(0) == "post_url" and column == 1:
                url = item.text(1)
                if url:
                    QDesktopServices.openUrl(QUrl(url))

        self.tree_widget.itemClicked.connect(open_url_on_click)

    def save_json_file(self):
        save_folder = os.path.join(os.path.dirname(__file__), 'save_data')
        os.makedirs(save_folder, exist_ok=True)

        now = datetime.now()
        timestamp = now.strftime('hour%H_minute%M_second%S_day%d_month%m_year%y')
        base_file_name = 'json_data'
        save_file_path = os.path.join(save_folder, f'{base_file_name}_{timestamp}.json')

        try:
            #
            data = []
            for i in range(self.tree_widget.topLevelItemCount()):
                item = self.tree_widget.topLevelItem(i)
                restaurant_dict = tree_to_dict(item)
                data.append(restaurant_dict)


            with open(save_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Success", f"File saved successfully to: {save_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")



