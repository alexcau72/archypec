from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QProgressBar, QListWidget, QPushButton, QStackedWidget, QMessageBox, QMenu, QLineEdit)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from app.ui.styles import DARK_STYLE, LIGHT_STYLE
from app.ui.tray_icon import ArchyPECTrayIcon
from app.ui.account_dialog import AccountDialog
from app.database import DatabaseManager
from app.archiver import Archiver
from app.imap_manager import IMAPManager
from app.utils.backup_manager import BackupManager
from app.utils.pdf_exporter import PDFExporter
import os

class SyncWorker(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, archiver, account_id):
        super().__init__()
        self.archiver = archiver
        self.account_id = account_id

    def run(self):
        try:
            self.archiver.sync_account(self.account_id)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchyPEC - Dashboard")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(DARK_STYLE)

        self.db_manager = DatabaseManager()
        self.archiver = Archiver(self.db_manager)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Sidebar
        self.sidebar = QVBoxLayout()
        self.dashboard_btn = QPushButton("Dashboard")
        self.archive_btn = QPushButton("Archivio")
        self.accounts_btn = QPushButton("Account")
        self.settings_btn = QPushButton("Impostazioni")

        self.sidebar.addWidget(self.dashboard_btn)
        self.sidebar.addWidget(self.archive_btn)
        self.sidebar.addWidget(self.accounts_btn)
        self.sidebar.addStretch()
        self.sidebar.addWidget(self.settings_btn)

        self.layout.addLayout(self.sidebar, 1)

        # Main Area
        self.main_area = QStackedWidget()
        self.layout.addWidget(self.main_area, 4)

        # 1. Dashboard View
        self.dashboard_view = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_view)
        dash_layout.addWidget(QLabel("<h2>Monitoraggio Spazio PEC</h2>"))

        self.quota_bar = QProgressBar()
        self.quota_bar.setValue(0)
        dash_layout.addWidget(self.quota_bar)
        self.quota_label = QLabel("Seleziona un account per aggiornare lo spazio.")
        dash_layout.addWidget(self.quota_label)

        self.refresh_quota_btn = QPushButton("Aggiorna Quota")
        dash_layout.addWidget(self.refresh_quota_btn)

        dash_layout.addStretch()
        self.main_area.addWidget(self.dashboard_view)

        # 2. Accounts View
        self.accounts_view = QWidget()
        acc_layout = QVBoxLayout(self.accounts_view)
        acc_layout.addWidget(QLabel("<h2>Gestione Account PEC</h2>"))
        self.acc_list = QListWidget()
        acc_layout.addWidget(self.acc_list)

        btn_layout = QHBoxLayout()
        self.add_acc_btn = QPushButton("Aggiungi Account")
        self.sync_btn = QPushButton("Sincronizza Ora")
        btn_layout.addWidget(self.add_acc_btn)
        btn_layout.addWidget(self.sync_btn)
        acc_layout.addLayout(btn_layout)

        self.main_area.addWidget(self.accounts_view)

        # 3. Archive View
        self.archive_view = QWidget()
        arch_layout = QVBoxLayout(self.archive_view)
        arch_layout.addWidget(QLabel("<h2>Messaggi Archiviati</h2>"))

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca nei messaggi (FTS5)...")
        self.search_bar.textChanged.connect(self.load_messages)
        arch_layout.addWidget(self.search_bar)

        self.msg_list = QListWidget()
        self.msg_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.msg_list.customContextMenuRequested.connect(self.on_archive_context_menu)
        arch_layout.addWidget(self.msg_list)
        self.main_area.addWidget(self.archive_view)

        # 4. Settings View
        self.settings_view = QWidget()
        set_layout = QVBoxLayout(self.settings_view)
        set_layout.addWidget(QLabel("<h2>Impostazioni e Manutenzione</h2>"))
        self.backup_btn = QPushButton("Esegui Backup Completo (ZIP)")
        self.toggle_theme_btn = QPushButton("Cambia Tema (Dark/Light)")
        self.cleanup_btn = QPushButton("Auto-Pulizia Server (> 6 mesi)")
        set_layout.addWidget(self.backup_btn)
        set_layout.addWidget(self.toggle_theme_btn)
        set_layout.addWidget(self.cleanup_btn)
        set_layout.addStretch()
        self.main_area.addWidget(self.settings_view)

        # Signals
        self.dashboard_btn.clicked.connect(lambda: self.main_area.setCurrentIndex(0))
        self.accounts_btn.clicked.connect(lambda: self.main_area.setCurrentIndex(1))
        self.archive_btn.clicked.connect(self.on_open_archive)
        self.settings_btn.clicked.connect(lambda: self.main_area.setCurrentIndex(3))

        self.add_acc_btn.clicked.connect(self.on_add_account)
        self.sync_btn.clicked.connect(self.on_sync_account)
        self.refresh_quota_btn.clicked.connect(self.on_refresh_quota)
        self.backup_btn.clicked.connect(self.on_backup)
        self.toggle_theme_btn.clicked.connect(self.on_toggle_theme)
        self.cleanup_btn.clicked.connect(self.on_cleanup)

        # Tray Icon
        self.tray_icon = ArchyPECTrayIcon(self)
        self.tray_icon.show()

        self.load_accounts()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            QMessageBox.information(self, "ArchyPEC", "L'applicazione continuerà a funzionare in background.")
            self.hide()
            event.ignore()

    def on_add_account(self):
        dialog = AccountDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Accounts (email, imap_server, port, username, password)
                    VALUES (?, ?, ?, ?, ?)
                ''', (data['email'], data['imap_server'], data['port'], data['username'], data['password']))
                conn.commit()
                conn.close()
                self.load_accounts()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile salvare l'account: {e}")

    def load_accounts(self):
        self.acc_list.clear()
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM Accounts")
        for row in cursor.fetchall():
            self.acc_list.addItem(f"{row[0]}: {row[1]}")
        conn.close()

    def on_sync_account(self):
        curr = self.acc_list.currentItem()
        if not curr:
            QMessageBox.warning(self, "Attenzione", "Seleziona un account da sincronizzare.")
            return

        acc_id = int(curr.text().split(":")[0])
        self.sync_btn.setEnabled(False)
        self.sync_worker = SyncWorker(self.archiver, acc_id)
        self.sync_worker.finished.connect(lambda: (self.sync_btn.setEnabled(True), QMessageBox.information(self, "Sincronizzazione", "Sincronizzazione completata!")))
        self.sync_worker.error.connect(lambda e: (self.sync_btn.setEnabled(True), QMessageBox.critical(self, "Errore", f"Errore durante la sincronizzazione: {e}")))
        self.sync_worker.start()

    def on_open_archive(self):
        self.main_area.setCurrentIndex(2)
        self.load_messages()

    def load_messages(self):
        self.msg_list.clear()
        query_text = self.search_bar.text().strip()
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        if query_text:
            cursor.execute('''
                SELECT id, subject, sender, date, file_path FROM Messages
                WHERE id IN (SELECT rowid FROM Messages_FTS WHERE Messages_FTS MATCH ?)
                ORDER BY date DESC
            ''', (query_text,))
        else:
            cursor.execute("SELECT id, subject, sender, date, file_path FROM Messages ORDER BY date DESC")

        for row in cursor.fetchall():
            item = f"{row[3]} - {row[1]} ({row[2]})"
            self.msg_list.addItem(item)
            self.msg_list.item(self.msg_list.count()-1).setData(Qt.UserRole, row[4])
        conn.close()

    def on_archive_context_menu(self, pos):
        item = self.msg_list.itemAt(pos)
        if not item: return

        menu = QMenu()
        export_pdf_action = menu.addAction("Esporta in PDF")
        restore_action = menu.addAction("Ripristina in Casella (Upload)")

        action = menu.exec(self.msg_list.mapToGlobal(pos))
        if action == export_pdf_action:
            eml_path = item.data(Qt.UserRole)
            if eml_path and os.path.exists(eml_path):
                pdf_path = eml_path.replace(".eml", ".pdf")
                PDFExporter.export_eml_to_pdf(eml_path, pdf_path)
                QMessageBox.information(self, "Esportazione", f"PDF creato in: {pdf_path}")
        elif action == restore_action:
            self.on_restore_message(item)

    def on_restore_message(self, item):
        curr_acc = self.acc_list.currentItem()
        if not curr_acc:
            QMessageBox.warning(self, "Attenzione", "Seleziona l'account di destinazione nella scheda Account.")
            return

        acc_id = int(curr_acc.text().split(":")[0])
        eml_path = item.data(Qt.UserRole)

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT imap_server, port, username, password FROM Accounts WHERE id=?", (acc_id,))
        acc = cursor.fetchone()
        conn.close()

        if acc and os.path.exists(eml_path):
            try:
                with open(eml_path, 'rb') as f:
                    content = f.read()
                imap = IMAPManager(acc[0], acc[1], acc[2], acc[3])
                imap.connect()
                imap.restore_message(content)
                imap.disconnect()
                QMessageBox.information(self, "Ripristino", "Messaggio ripristinato con successo sul server.")
            except Exception as e:
                QMessageBox.critical(self, "Errore Ripristino", str(e))

    def on_refresh_quota(self):
        curr = self.acc_list.currentItem()
        if not curr:
            QMessageBox.warning(self, "Attenzione", "Seleziona un account nella scheda Account.")
            return

        acc_id = int(curr.text().split(":")[0])
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT imap_server, port, username, password FROM Accounts WHERE id=?", (acc_id,))
        acc = cursor.fetchone()
        conn.close()

        if acc:
            try:
                imap = IMAPManager(acc[0], acc[1], acc[2], acc[3])
                imap.connect()
                quota = imap.get_quota()
                imap.disconnect()
                if quota:
                    try:
                        # Extract usage and limit - imapclient get_quota returns a list of Quota objects/tuples
                        # Example: [(u'INBOX', (u'STORAGE', 1234, 5000))]
                        # usage is index 1 of the inner tuple, limit is index 2
                        resource_info = quota[0][1] # (u'STORAGE', 1234, 5000)
                        usage = resource_info[1]
                        limit = resource_info[2]
                        perc = int((usage / limit) * 100)
                        self.quota_bar.setValue(perc)
                        self.quota_label.setText(f"Utilizzo: {usage/1024:.2f} MB / {limit/1024:.2f} MB ({perc}%)")
                    except:
                         self.quota_label.setText(f"Dati quota: {quota}")
                else:
                    self.quota_label.setText("Quota non supportata dal server.")
            except Exception as e:
                QMessageBox.critical(self, "Errore Quota", f"Impossibile recuperare la quota: {e}")

    def on_backup(self):
        try:
            path = BackupManager.create_full_backup()
            QMessageBox.information(self, "Backup", f"Backup creato con successo: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Errore Backup", str(e))

    def on_toggle_theme(self):
        if self.styleSheet() == DARK_STYLE:
            self.setStyleSheet(LIGHT_STYLE)
        else:
            self.setStyleSheet(DARK_STYLE)

    def on_cleanup(self):
        curr = self.acc_list.currentItem()
        if not curr:
            QMessageBox.warning(self, "Attenzione", "Seleziona un account nella scheda Account.")
            return

        acc_id = int(curr.text().split(":")[0])
        reply = QMessageBox.question(self, "Conferma", "Vuoi davvero eliminare dal server i messaggi più vecchi di 6 mesi (solo se già archiviati localmente)?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT imap_server, port, username, password FROM Accounts WHERE id=?", (acc_id,))
            acc = cursor.fetchone()
            conn.close()

            if acc:
                try:
                    imap = IMAPManager(acc[0], acc[1], acc[2], acc[3])
                    imap.connect()
                    count = self.archiver.run_retention_policy(acc_id, imap)
                    imap.disconnect()
                    QMessageBox.information(self, "Auto-Pulizia", f"Eliminati {count} messaggi dal server.")
                except Exception as e:
                    QMessageBox.critical(self, "Errore Pulizia", str(e))

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
