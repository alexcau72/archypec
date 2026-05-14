from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon

class ArchyPECTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon.fromTheme("mail-unread")) # Placeholder icon
        self.setToolTip("ArchyPEC - Monitoring active")

        menu = QMenu(parent)
        restore_action = menu.addAction("Apri ArchyPEC")
        restore_action.triggered.connect(self.on_restore)

        exit_action = menu.addAction("Esci")
        exit_action.triggered.connect(self.on_exit)

        self.setContextMenu(menu)

    def on_restore(self):
        if self.parent():
            self.parent().showNormal()
            self.parent().activateWindow()

    def on_exit(self):
        import sys
        sys.exit()
