import sys
import requests
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from CustomWidgets.SignUpDialog import SignUpDialog

class LoginDialog(QDialog):
    def __init__(self, login_url, sign_up_url):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(300, 200)
        self.login_url = login_url
        self.sign_up_url = sign_up_url
        self.access_token = None
        
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
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        
        # Nút Đăng ký
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.open_register_dialog)
        layout.addWidget(self.register_button)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        url = self.login_url
        payload = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json().get('data')
                self.access_token = data['accessToken']
                QMessageBox.information(self, "Success", "Login successful!")
                self.accept()
            else:
                print(response.status_code)
                print(response.json())
                QMessageBox.warning(self, "Error", "Invalid username or password")
        
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to connect to server: {e}")

    def open_register_dialog(self):
        # Mở dialog đăng ký
        sign_up_dialog = SignUpDialog(self.sign_up_url)
        sign_up_dialog.exec_()

# Main function
def main():
    app = QApplication(sys.argv)
    
    # Hiển thị pop-up đăng nhập
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        print("Logged in successfully!")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
