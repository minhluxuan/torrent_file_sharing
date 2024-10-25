import sys
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dynamic Input Dialog')
        self.setGeometry(100, 100, 300, 300)

        # Layout để chứa các input
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Danh sách để lưu các trường nhập liệu
        self.inputs = []

        # Nút để thêm input mới
        self.add_button = QPushButton('Add Tracker', self)
        self.add_button.clicked.connect(self.add_input)
        self.layout.addWidget(self.add_button)

        # Nút để xác nhận và lấy giá trị từ các input
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.submit_inputs)
        self.layout.addWidget(self.submit_button)

        self.values = []

    def add_input(self):
        # Tạo một QLineEdit mới và thêm vào layout
        input_field = QLineEdit(self)
        self.layout.addWidget(input_field)
        self.inputs.append(input_field)

    def submit_inputs(self):
        self.values = [input_field.text() for input_field in self.inputs]
        
        # QMessageBox.information(self, 'Submitted Values', '\n'.join(self.values), QMessageBox.Ok)
        self.accept()

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 300, 200)

        # Tạo nút để mở dialog
        btn = QPushButton('Open Input Dialog', self)
        btn.clicked.connect(self.open_dialog)
        btn.resize(btn.sizeHint())
        btn.move(100, 70)

    def open_dialog(self):
        dialog = InputDialog()
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
