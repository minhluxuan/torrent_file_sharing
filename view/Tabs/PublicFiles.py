import os
import shutil
from urllib.parse import parse_qs, urlparse
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QLineEdit, QTableWidget, 
                             QTableWidgetItem,QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QDialog)
from CustomWidgets.InputDialog import InputDialog
from modules.main import publish, fetch_file, download
from CustomWidgets.MagnetLinkDialog import MagnetLinkDialog
from modules.helper import generate_info_hash
import os
from CustomWidgets.LoginDialog import LoginDialog
from token_store import set_token, get_token

class PublicFiles(QtWidgets.QWidget):

    play = QtCore.pyqtSignal(object)
    addFavourite = QtCore.pyqtSignal(object)
    addToCollection = QtCore.pyqtSignal(object, bool)
    playlist_added = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(PublicFiles, self).__init__(*args, **kwargs)

        self.dirs = set()
        self.music_files = list()
        self.file_path = list()
        self.num_rows = 0

        self.initUI()

    def initUI(self):
        self.setLayout(QtWidgets.QVBoxLayout())

        self.setObjectName("My File")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Filename", "Type", "Size", "Download", "Get Magnet Link"])

        self.tracker_connect_layout = QHBoxLayout()
        self.tracker_connect_input = QLineEdit()
        self.tracker_connect_input.setPlaceholderText("Please enter tracker's url first...")
        self.tracker_connect_button = QPushButton('Connect', self)
        self.tracker_connect_button.clicked.connect(self.connect_to_tracker_and_get_files)
        self.tracker_connect_layout.addWidget(self.tracker_connect_input)
        self.tracker_connect_layout.addWidget(self.tracker_connect_button)

        self.download_file_layout = QHBoxLayout()
        self.magnet_link_input = QLineEdit()
        self.magnet_link_input.setPlaceholderText("Or enter magnet link to download...")
        self.download_button = QPushButton('Download', self)
        self.download_button.clicked.connect(self.download_by_magnet_link)
        self.download_file_layout.addWidget(self.magnet_link_input)
        self.download_file_layout.addWidget(self.download_button)

        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter file name to search...")
        self.search_layout.addWidget(self.search_input)
        self.search_input.textChanged.connect(self.search_file)

        self.layout().setSpacing(20)
        self.layout().setContentsMargins(*[10]*4)
        self.layout().addLayout(self.tracker_connect_layout)
        self.layout().addLayout(self.download_file_layout)
        self.layout().addLayout(self.search_layout)
        self.layout().addWidget(self.table)

    def search(self, string):
        if not string:
            self.stack_view.setCurrentIndex(0)
            return

        if self.stack_view.currentIndex() == 0:
            self.stack_view.setCurrentIndex(1)

        widgets = self.view.widgets()

        self.search_display_widget.removeTileParent()
        self.search_display_widget.deleteAll()
        for tile in widgets:
            if tile.getTitle().lower().startswith(string.lower()):
                self.search_display_widget.addMusicTile(tile)

    def addSearchDir(self, dir):
        self.dirs.add(dir)

    def deleteSearchDir(self, dirs):
        try:
            self.dirs.remove(dirs)

        except KeyError:
            pass

        self.loadFiles()

    def add_table_row(self, info_hash, file_name, file_type, file_size):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        self.table.setItem(row_position, 0, QTableWidgetItem(file_name))
        self.table.setItem(row_position, 1, QTableWidgetItem(file_type))
        self.table.setItem(row_position, 2, QTableWidgetItem(str(file_size)))
        
        download_button = QPushButton('Download')
        get_magnet_link_button = QPushButton('Get magnet link')
        
        # Get tracker_urls from Input Dialog here
        download_button.clicked.connect(lambda: self.download_file(info_hash))
        get_magnet_link_button.clicked.connect(lambda: self.get_magnet_link(info_hash, file_name))
        
        self.table.setCellWidget(row_position, 3, download_button)
        self.table.setCellWidget(row_position, 4, get_magnet_link_button)
        self.num_rows += 1

    def upload_file(self):
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(self, "Chọn file để upload", "", "All Files (*.*)")

        if file_paths:
            destination_dir = os.path.abspath("../storage")
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                file_size = self.get_file_size(file_path)
                file_type = self.get_file_type(file_name)

                destination_path = os.path.join(destination_dir, file_name)

                shutil.copy2(file_path, destination_path)

                self.add_table_row(file_name, file_type, file_size)

    def delete_row(self, row_position):
        # Xóa hàng tương ứng
        self.table.removeRow(row_position)
        print(f"Đã xóa hàng {row_position}")

    def get_file_size(self, file_path):
        # Lấy kích thước file theo KB, MB, GB
        size = os.path.getsize(file_path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size // 1024} KB"
        elif size < 1024 ** 3:
            return f"{size // (1024 ** 2)} MB"
        else:
            return f"{size // (1024 ** 3)} GB"

    def get_file_type(self, file_name):
        # Lấy loại file từ đuôi mở rộng
        return file_name.split('.')[-1].upper() + " File"

    def download_file(self, info_hash):
        dialog = InputDialog()
        dialog.exec_()
        tracker_urls = dialog.values
        download(info_hash, tracker_urls)

    def search_file(self):
        # Lấy tên file cần tìm từ ô nhập
        search_text = self.search_input.text()
        # Tìm kiếm file trong bảng
        for row in range(self.table.rowCount()):
            file_name = self.table.item(row, 0).text()
            # Kiểm tra xem file có chứa chuỗi tìm kiếm không
            if search_text in file_name:
                # Hiển thị hàng nếu tìm thấy
                self.table.setRowHidden(row, False)
            else:
                # Ẩn các hàng không khớp
                self.table.setRowHidden(row, True)

    def connect_to_tracker_and_get_files(self):
        tracker_url = self.tracker_connect_input.text()
        status_code, files = fetch_file(tracker_url, get_token(tracker_url))

        if status_code == 401:
            login_dialog = LoginDialog(f'{tracker_url}/auth/login', f'{tracker_url}/auth/signup')
            if login_dialog.exec_() == QDialog.Accepted:
                set_token(tracker_url, login_dialog.access_token)

                status_code, files = fetch_file(tracker_url, get_token(tracker_url))
            else:
                return

        self.table.setRowCount(0)

        self.num_rows = 0

        for file in files:
            file_type = self.get_file_type(file['name'])
            self.add_table_row(file['infoHash'], file['name'], file_type, file['size'])
        
        print(self.num_rows)

    def parse_magnet_link(self, magnet_link):
        parsed_link = urlparse(magnet_link)
        
        if parsed_link.scheme != 'magnet':
            raise ValueError("Not a valid magnet link")
        
        params = parse_qs(parsed_link.query)
        
        info_hash = params.get('xt', [None])[0]
        if info_hash and info_hash.startswith("urn:btih:"):
            info_hash = info_hash[9:]
        
        filename = params.get('dn', [None])[0]
        tracker_urls = params.get('tr', [])

        return info_hash, filename, tracker_urls

    def download_by_magnet_link(self):
        magnet_link = self.magnet_link_input.text()
        
        info_hash, file_name, tracker_urls = self.parse_magnet_link(magnet_link)
        download(info_hash, tracker_urls)

    def get_magnet_link(self, info_hash, file_name):
        dialog = InputDialog()
        dialog.exec_()
        tracker_urls = dialog.values
        
        magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={file_name}"
    
        for tracker in tracker_urls:
            magnet_link += f"&tr={tracker}"
        
        magnet_link_dialog = MagnetLinkDialog(magnet_link)
        magnet_link_dialog.exec_()