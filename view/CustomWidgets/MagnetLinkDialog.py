import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox

class MagnetLinkDialog(QDialog):
    def __init__(self, magnet_link, parent=None):
        super().__init__(parent)
        self.magnet_link = magnet_link
        self.setWindowTitle("Magnet Link")
        self.resize(400, 150)
        
        # Create the layout
        layout = QVBoxLayout(self)
        
        # Display the magnet link
        self.label = QLabel("Magnet Link:", self)
        layout.addWidget(self.label)
        
        self.link_edit = QLineEdit(self)
        self.link_edit.setText(magnet_link)
        self.link_edit.setReadOnly(True)
        layout.addWidget(self.link_edit)
        
        # Copy button
        self.copy_button = QPushButton("Copy", self)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)
    
    def copy_to_clipboard(self):
        # Copy the magnet link to the clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(self.magnet_link)
        
        # Notify that the link was copied
        QMessageBox.information(self, "Copied", "Magnet link copied to clipboard!")