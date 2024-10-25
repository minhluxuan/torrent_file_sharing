import os
import shutil
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QLineEdit, QTableWidget, 
                             QTableWidgetItem,QHBoxLayout, QPushButton, QFileDialog, QMessageBox)
from CustomWidgets.InputDialog import InputDialog
from modules.main import publish
from modules.helper import generate_info_hash
from CustomWidgets.MagnetLinkDialog import MagnetLinkDialog

class MyFiles(QtWidgets.QWidget): 
    play = QtCore.pyqtSignal(object)
    addFavourite = QtCore.pyqtSignal(object)
    addToCollection = QtCore.pyqtSignal(object, bool)
    playlist_added = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(MyFiles, self).__init__(*args, **kwargs)

        self.dirs = set()
        self.music_files = list()
        self.file_path = list()

        self.initUI()

    def initUI(self):
        self.setLayout(QtWidgets.QVBoxLayout())

        self.setObjectName("My File")

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Filename", "Type", "Size", "Publish", "Delete", "Get Magnet Link"])

        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter file name to search...")
        self.search_layout.addWidget(self.search_input)
        self.search_input.textChanged.connect(self.search_file)

        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)

        self.layout().setSpacing(20)
        self.layout().setContentsMargins(*[10]*4)
        self.layout().addLayout(self.search_layout)
        self.layout().addWidget(self.table)
        self.layout().addWidget(self.upload_button)

        self.load_files_from_storage()

    def load_files_from_storage(self):
        storage_dir = "../storage"

        self.table.setRowCount(0)

        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

        for file_name in os.listdir(storage_dir):
            file_path = os.path.join(storage_dir, file_name)

            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_type = self.get_file_type(file_name)
                self.add_table_row(file_name, file_type, file_size)

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

    def add_table_row(self, file_name, file_type, file_size):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        self.table.setItem(row_position, 0, QTableWidgetItem(file_name))
        self.table.setItem(row_position, 1, QTableWidgetItem(file_type))
        self.table.setItem(row_position, 2, QTableWidgetItem(str(file_size)))
        
        publish_button = QPushButton('Publish')
        publish_button.clicked.connect(lambda: self.publish_file(file_name))

        delete_button = QPushButton('Delete')
        delete_button.clicked.connect(lambda _, row=row_position: self.delete_row(row))
        
        get_magnet_link_button = QPushButton('Get Magnet Link')
        get_magnet_link_button.clicked.connect(lambda _, row=row_position: self.get_magnet_link(file_name))
        
        self.table.setCellWidget(row_position, 4, delete_button)
        self.table.setCellWidget(row_position, 3, publish_button)
        self.table.setCellWidget(row_position, 5, get_magnet_link_button)

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

    def publish_file(self, file_name):
        dialog = InputDialog()
        dialog.exec_()
        tracker_urls = dialog.values
        file_path = os.path.abspath(f'../storage/{file_name}')
        publish(file_path, tracker_urls)

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

    def get_magnet_link(self, file_name):
        dialog = InputDialog()
        dialog.exec_()
        tracker_urls = dialog.values
        
        file_path = os.path.abspath(f'../storage/{file_name}')
        info_hash = generate_info_hash(file_path)
        magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={file_name}"
    
        for tracker in tracker_urls:
            magnet_link += f"&tr={tracker}"
        
        magnet_link_dialog = MagnetLinkDialog(magnet_link)
        magnet_link_dialog.exec_()
