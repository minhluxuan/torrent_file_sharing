import sys
import requests
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class SignUpDialog(QDialog):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("Sign Up")
        self.resize(300, 250)
        self.url = url
        
        layout = QVBoxLayout()
        
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        
        self.first_name_label = QLabel("First name:")
        self.first_name_input = QLineEdit()
        layout.addWidget(self.first_name_label)
        layout.addWidget(self.first_name_input)

        self.last_name_label = QLabel("Last name:")
        self.last_name_input = QLineEdit()
        layout.addWidget(self.last_name_label)
        layout.addWidget(self.last_name_input)
        
        self.signup_button = QPushButton("Sign Up")
        self.signup_button.clicked.connect(self.sign_up)
        layout.addWidget(self.signup_button)
        
        self.setLayout(layout)

    def sign_up(self):
        username = self.username_input.text()
        password = self.password_input.text()
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()

        url = self.url  # Thay đổi đường dẫn nếu cần
        payload = {
            "username": username,
            "password": password,
            "firstName": first_name,
            "lastName": last_name
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 201:  # Thay đổi mã trạng thái tùy thuộc vào API
                print(response.status_code)
                print(response.json())
                QMessageBox.information(self, "Success", "Registration successful! Please log in.")
                self.accept()
            else:
                print(response.status_code)
                print(response.json())
                QMessageBox.warning(self, "Error", "Registration failed. Please check your details.")
        
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to connect to server: {e}")
