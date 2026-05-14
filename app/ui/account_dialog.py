from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QLineEdit, QDialogButtonBox, QLabel)

class AccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggiungi Account PEC")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()

        self.email_input = QLineEdit()
        self.server_input = QLineEdit()
        self.port_input = QLineEdit()
        self.port_input.setText("993")
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)

        self.form.addRow("Email PEC:", self.email_input)
        self.form.addRow("Server IMAP:", self.server_input)
        self.form.addRow("Porta:", self.port_input)
        self.form.addRow("Username:", self.user_input)
        self.form.addRow("Password:", self.pass_input)

        self.layout.addLayout(self.form)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        return {
            "email": self.email_input.text(),
            "imap_server": self.server_input.text(),
            "port": int(self.port_input.text()),
            "username": self.user_input.text(),
            "password": self.pass_input.text()
        }
