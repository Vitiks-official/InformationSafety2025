import sys
import threading
import time
import psutil
from pprint import pprint

from pyexpat.errors import messages
from screeninfo import get_monitors
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QListWidget, QAbstractItemView
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt
from StyleSheets import *


mode = 0
input_output = psutil.net_io_counters(pernic=False)
input_output_with_pernic = psutil.net_io_counters(pernic=True)
stats_dict1, stats_dict2 = {}, {}


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Network Traffic Usage")
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
        self.main_text.setText("Network Traffic Usage")
        self.main_text.setStyleSheet("color: #c6dbba")

        self.total_network_usage_button = QPushButton(self)
        self.total_network_usage_button.setGeometry(20, 120, 261, 51)
        self.total_network_usage_button.setText("Total")
        self.total_network_usage_button.setStyleSheet(button_style)
        self.total_network_usage_button.clicked.connect(self.click)

        self.per_network_interface_button = QPushButton(self)
        self.per_network_interface_button.setGeometry(620, 120, 261, 51)
        self.per_network_interface_button.setText("Per Interface")
        self.per_network_interface_button.setStyleSheet(button_style)
        self.per_network_interface_button.clicked.connect(self.click)

        self.per_process_button = QPushButton(self)
        self.per_process_button.setGeometry(320, 120, 261, 51)
        self.per_process_button.setText("Per Process")
        self.per_process_button.setStyleSheet(button_style)
        self.per_process_button.clicked.connect(self.click)

        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(30, 200, 841, 371)
        self.listWidget.setFont(QFont("Cuprum", 20))
        self.listWidget.setStyleSheet(list_style)
        self.listWidget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

    def click(self):
        global mode
        if self.sender().text() == "Total":
            mode = 1
        elif self.sender().text() == "Per Interface":
            mode = 2
        elif self.sender().text() == "Per Process":
            mode = 3


def get_bytes_count(bytes):
    for i in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{i}B"
        bytes /= 1024


def total_network_usage():
    global input_output
    input_output2 = psutil.net_io_counters()
    dif_sent_stats = input_output2.bytes_sent - input_output.bytes_sent
    dif_recv_stats = input_output2.bytes_recv - input_output.bytes_recv
    message = '\n'.join([f"Upload:             \t\t{get_bytes_count(input_output2.bytes_sent)}",
                        f"DownLoad:        \t\t{get_bytes_count(input_output2.bytes_recv)}",
                        f"Upload speed:   \t\t{get_bytes_count(dif_sent_stats / 1)}",
                        f"Download speed:\t\t{get_bytes_count(dif_recv_stats / 1)}"])
    input_output = psutil.net_io_counters()
    main_window.listWidget.clear()
    main_window.listWidget.addItem(message)


def per_network_interface():
    global input_output_with_pernic
    input_output_with_pernic2 = psutil.net_io_counters(pernic=True)
    scroll_position = main_window.listWidget.verticalScrollBar().value()
    main_window.listWidget.clear()
    for name, input_output_stat in input_output_with_pernic.items():
        upload_speed, download_speed = (input_output_with_pernic2[name].bytes_sent - input_output_stat.bytes_sent,
                                        input_output_with_pernic2[name].bytes_recv - input_output_stat.bytes_recv)
        message = '\n'.join([f"{name}",
                                f"\tDownload:            \t\t{get_bytes_count(input_output_with_pernic2[name].bytes_recv)}",
                                f"\tUpload:                \t\t{get_bytes_count(input_output_with_pernic2[name].bytes_sent)}",
                                f"\tUpload speed:       \t\t{get_bytes_count(upload_speed / 1)}",
                                f"\tDownload speed:   \t\t{get_bytes_count(download_speed / 1)}"])
        main_window.listWidget.addItem(message)
    main_window.listWidget.verticalScrollBar().setValue(scroll_position)
    input_output_with_pernic = input_output_with_pernic2


def per_process():
    global stats_dict1, stats_dict2
    try:
        for i in psutil.process_iter():
            if "started" in str(i) and i.status() == "running":
                if i.name in stats_dict1:
                    stats_dict1[i.name()][1] += i.io_counters().read_bytes
                    stats_dict1[i.name()][2] += i.io_counters().write_bytes
                else:
                    stats_dict1[i.name()] = [i.pid, i.io_counters().read_bytes, i.io_counters().write_bytes]
        scroll_position = main_window.listWidget.verticalScrollBar().value()
        main_window.listWidget.clear()
        if not stats_dict2:
            for i in stats_dict1:
                message = "\n".join([f"pid: {stats_dict1[i][0]}",
                                     f"name: {i}",
                                     f"Upload: {get_bytes_count(stats_dict1[i][2])}",
                                     f"Download: {get_bytes_count(stats_dict1[i][1])}",
                                     f"Upload speed: 0.00B",
                                     f"Download speed: 0.00B"])
                main_window.listWidget.addItem(message)
        else:
            for i in stats_dict1:
                message = "\n".join([f"pid: {stats_dict1[i][0]}",
                                     f"name: {i}",
                                     f"Upload: {get_bytes_count(stats_dict1[i][2])}",
                                     f"Download: {get_bytes_count(stats_dict1[i][1])}",
                                     f"Upload speed: {get_bytes_count(stats_dict1[i][2] - stats_dict2[i][2])}",
                                     f"Download speed: {get_bytes_count(stats_dict1[i][1] - stats_dict2[i][1])}"])
                main_window.listWidget.addItem(message)
        main_window.listWidget.verticalScrollBar().setValue(scroll_position)
        stats_dict2 = stats_dict1.copy()
    except Exception:
        pass


def main_loop():
    while True:
        time.sleep(1)
        if mode == 1:
            total_network_usage()
        elif mode == 2:
            per_network_interface()
        elif mode == 3:
            per_process()


t = threading.Thread(target=main_loop)
t.daemon = True
t.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())