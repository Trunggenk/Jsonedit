import sys
from PyQt5.QtWidgets import QApplication
from views.json_viewer import JSONViewer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JSONViewer()
    window.show()
    sys.exit(app.exec_())
