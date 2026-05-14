import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path='data/archypec_main.db'):
        self.db_path = db_path
        # Ensure data directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                imap_server TEXT NOT NULL,
                port INTEGER NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                last_sync TIMESTAMP
            )
        ''')

        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                message_id TEXT,
                subject TEXT,
                sender TEXT,
                date TIMESTAMP,
                body_plain TEXT,
                file_path TEXT,
                is_local INTEGER DEFAULT 0,
                FOREIGN KEY (account_id) REFERENCES Accounts(id)
            )
        ''')

        # FTS5 for full-text search on messages
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS Messages_FTS USING fts5(
                subject, sender, body_plain, content='Messages', content_rowid='id'
            )
        ''')

        # Attachments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                filename TEXT,
                file_path TEXT,
                size INTEGER,
                FOREIGN KEY (message_id) REFERENCES Messages(id)
            )
        ''')

        # Threads table (links PEC to its receipts)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_message_id TEXT,
                receipt_message_id TEXT,
                receipt_type TEXT, -- 'accettazione' or 'consegna'
                UNIQUE(parent_message_id, receipt_message_id)
            )
        ''')

        # Triggers for FTS5 synchronization
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON Messages BEGIN
                INSERT INTO Messages_FTS(rowid, subject, sender, body_plain)
                VALUES (new.id, new.subject, new.sender, new.body_plain);
            END;
        ''')
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON Messages BEGIN
                INSERT INTO Messages_FTS(Messages_FTS, rowid, subject, sender, body_plain)
                VALUES('delete', old.id, old.subject, old.sender, old.body_plain);
            END;
        ''')
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON Messages BEGIN
                INSERT INTO Messages_FTS(Messages_FTS, rowid, subject, sender, body_plain)
                VALUES('delete', old.id, old.subject, old.sender, old.body_plain);
                INSERT INTO Messages_FTS(rowid, subject, sender, body_plain)
                VALUES(new.id, new.subject, new.sender, new.body_plain);
            END;
        ''')

        conn.commit()
        conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    print("Database initialized successfully.")
