import os
import mailparser
from datetime import datetime
from app.database import DatabaseManager
from app.imap_manager import IMAPManager

class Archiver:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def sync_account(self, account_id):
        """Downloads all messages from the server that are not yet local."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email, imap_server, port, username, password FROM Accounts WHERE id = ?", (account_id,))
        acc = cursor.fetchone()
        if not acc:
            return

        email, server, port, user, password = acc
        imap = IMAPManager(server, port, user, password)
        try:
            imap.connect()
            msg_ids = imap.fetch_messages_ids()

            for msg_id in msg_ids:
                # Check if already in DB
                cursor.execute("SELECT id FROM Messages WHERE account_id = ? AND message_id = ?", (account_id, str(msg_id)))
                if cursor.fetchone():
                    continue

                # Download and archive
                eml_content = imap.download_message(msg_id)
                self.archive_message(account_id, msg_id, eml_content)

            # Post-sync: link receipts to parents
            self.link_pec_receipts(account_id)

            imap.disconnect()
        except Exception as e:
            print(f"Sync error for {email}: {e}")
        finally:
            conn.close()

    def archive_message(self, account_id, msg_id, eml_content, storage_root='storage'):
        """Parses, saves, and indexes a message."""
        mail = mailparser.parse_from_bytes(eml_content)

        # Determine path: storage/account_id/year/month/msg_id.eml
        date_obj = mail.date or datetime.now()
        year = str(date_obj.year)
        month = f"{date_obj.month:02d}"

        rel_dir = os.path.join(str(account_id), year, month)
        abs_dir = os.path.join(storage_root, rel_dir)
        os.makedirs(abs_dir, exist_ok=True)

        file_name = f"{msg_id}.eml"
        abs_path = os.path.join(abs_dir, file_name)

        with open(abs_path, 'wb') as f:
            f.write(eml_content)

        # Index in DB
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        sender = ""
        if mail.from_:
            sender = mail.from_[0][1] if len(mail.from_[0]) > 1 else mail.from_[0][0]

        cursor.execute('''
            INSERT INTO Messages (account_id, message_id, subject, sender, date, body_plain, file_path, is_local)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (account_id, str(msg_id), mail.subject, sender,
              date_obj, mail.text_plain[0] if mail.text_plain else "", abs_path))

        db_msg_id = cursor.lastrowid

        # Save attachments info
        for att in mail.attachments:
            cursor.execute('''
                INSERT INTO Attachments (message_id, filename, file_path, size)
                VALUES (?, ?, ?, ?)
            ''', (db_msg_id, att.get('filename'), "", att.get('size')))

        conn.commit()
        conn.close()
        return abs_path

    def link_pec_receipts(self, account_id):
        """Simple logic to link PEC receipts to original messages via Message-ID or subject."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # In PEC, receipts often have 'CONSEGNA: ...' or 'ACCETTAZIONE: ...' and reference the original ID
        # This is a simplified heuristic
        cursor.execute("SELECT id, message_id, subject FROM Messages WHERE account_id = ?", (account_id,))
        messages = cursor.fetchall()

        for mid, msg_id, subject in messages:
            rtype = None
            if subject.startswith("ACCETTAZIONE:"): rtype = "accettazione"
            elif subject.startswith("CONSEGNA:"): rtype = "consegna"

            if rtype:
                # Try to find parent message by original subject
                parent_subject = subject.replace("ACCETTAZIONE:", "").replace("CONSEGNA:", "").strip()
                cursor.execute("SELECT message_id FROM Messages WHERE subject = ? AND account_id = ? AND id != ?", (parent_subject, account_id, mid))
                parent = cursor.fetchone()
                if parent:
                    cursor.execute('''
                        INSERT OR IGNORE INTO Threads (parent_message_id, receipt_message_id, receipt_type)
                        VALUES (?, ?, ?)
                    ''', (parent[0], msg_id, rtype))

        conn.commit()
        conn.close()

    def run_retention_policy(self, account_id, imap_manager, months=6):
        """Identifies and deletes old messages from server if archived locally."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(f'''
            SELECT message_id FROM Messages
            WHERE account_id = ?
            AND is_local = 1
            AND date < date('now', '-{months} months')
        ''', (account_id,))

        to_delete = [row[0] for row in cursor.fetchall()]

        if to_delete:
            imap_manager.delete_messages(to_delete)

        conn.close()
        return len(to_delete)
