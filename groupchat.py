import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QTimer
from skpy import Skype, SkypeChats, SkypeGroupChat
import time

class SkypeMessageSender(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Skype Message Sender")
        self.setup_ui()
        self.skype = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_periodic_messages)

    def setup_ui(self):
        layout = QVBoxLayout()

        self.email_label = QLabel("Email:")
        layout.addWidget(self.email_label)
        self.email_entry = QLineEdit()
        layout.addWidget(self.email_entry)

        self.password_label = QLabel("Password:")
        layout.addWidget(self.password_label)
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red")
        layout.addWidget(self.error_label)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.authenticate)
        layout.addWidget(self.login_button)

        self.group_label = QLabel("Select Groups:")
        layout.addWidget(self.group_label)
        self.group_list = QListWidget()
        self.group_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.group_list)

        self.message_label = QLabel("Enter Message:")
        layout.addWidget(self.message_label)
        self.message_entry = QTextEdit()
        layout.addWidget(self.message_entry)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_sending)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        self.message_entry.setEnabled(False)
        self.send_button.setEnabled(False)

    def authenticate(self):
        email = self.email_entry.text()
        password = self.password_entry.text()

        try:
            self.skype = Skype(email, password)
            self.error_label.setText("Authentication successful")
            self.fetch_group_names()
            self.login_button.setEnabled(False)
            self.message_entry.setEnabled(True)
            self.send_button.setEnabled(True)
        except Exception as e:
            self.error_label.setText(f"Authentication failed: {e}")

    def fetch_group_names(self):
        
        self.group_list.clear()
        skchats = SkypeChats(self.skype)

        groupChats = []

        while True:
            recent_chats = skchats.recent()
            if not recent_chats or len(recent_chats) == 0:
                print("No recent chats found. Waiting for new chats...")
                break
            else:
                for chat_id, chat_obj in recent_chats.items():
                    if isinstance(chat_obj, SkypeGroupChat):
                        groupChats.append(chat_obj)
                
            time.sleep(1)

        for group_chat in groupChats:
            if group_chat.open and group_chat.active:
                item = QListWidgetItem(group_chat.topic)
                item.setData(Qt.UserRole, group_chat.id)
                self.group_list.addItem(item)

    def send_message(self):
        selected_items = self.group_list.selectedItems()
        message = self.message_entry.toPlainText()

        for item in selected_items:
            chat_id = item.data(Qt.UserRole)
            chat = self.skype.chats[chat_id]
            chat.sendMsg(message)
        self.timer.start(60*60*3) 
        self.send_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def send_periodic_messages(self):
        selected_items = self.group_list.selectedItems()
        message = self.message_entry.toPlainText()

        for item in selected_items:
            chat_id = item.data(Qt.UserRole)
            chat = self.skype.chats[chat_id]
            chat.sendMsg(message)
            print("Periodic message sent to", chat.topic)

    def stop_sending(self):
        self.timer.stop()
        self.stop_button.setEnabled(False)
        self.send_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SkypeMessageSender()
    window.show()
    sys.exit(app.exec_())
