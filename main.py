import sys
import psutil
import time
from screeninfo import get_monitors
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QListWidget
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt
from StyleSheets import *


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Network Traffic")
        self.setFixedSize(900, 600)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/main_background.jpg'))
        self.setWindowIcon(QIcon("images/MainWindowIcon.png"))

        font = QFont()
        font.setFamily("Cuprum")

        font.setPointSize(40)
        self.main_text = QLabel(self)
        self.main_text.setGeometry(0, 20, 891, 81)
        self.main_text.setFont(font)
        self.main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_text.setText("Network Traffic")
        self.main_text.setStyleSheet("color: #c6dbba")

        self.total_network_usage_button = QPushButton(self)
        self.total_network_usage_button.setGeometry(20, 120, 261, 51)
        self.total_network_usage_button.setText("Total")
        self.total_network_usage_button.setStyleSheet(button_style)
        self.total_network_usage_button.clicked.connect(self.total_network_usage)

        self.per_network_interface_button = QPushButton(self)
        self.per_network_interface_button.setGeometry(620, 120, 261, 51)
        self.per_network_interface_button.setText("Per Interface")
        self.per_network_interface_button.setStyleSheet(button_style)
        self.per_network_interface_button.clicked.connect(self.per_network_interface)

        self.per_process_button = QPushButton(self)
        self.per_process_button.setGeometry(320, 120, 261, 51)
        self.per_process_button.setText("Per Process")
        self.per_process_button.setStyleSheet(button_style)
        self.per_process_button.clicked.connect(self.per_process)

        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(30, 200, 841, 371)

    def get_bytes_count(self, bytes):
        for i in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f"{bytes:.2f}{i}B"
            bytes /= 1024

    def total_network_usage(self):
        io = psutil.net_io_counters()
        bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv
        while True:
            time.sleep(1)
            io_2 = psutil.net_io_counters()
            us, ds = io_2.bytes_sent - bytes_sent, io_2.bytes_recv - bytes_recv
            print(f"Upload: {self.get_bytes_count(io_2.bytes_sent)}   "
                  f", Download: {self.get_bytes_count(io_2.bytes_recv)}   "
                  f", Upload Speed: {self.get_bytes_count(us / 1)}/s   "
                  f", Download Speed: {self.get_bytes_count(ds / 1)}/s      ")
            bytes_sent, bytes_recv = io_2.bytes_sent, io_2.bytes_recv

    def per_network_interface(self):
        sen

    def per_process(self):
        pass




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())