import unittest
import os
import sqlite3
from app.database import DatabaseManager

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_path = 'data/test_archypec.db'
        self.db_manager = DatabaseManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_tables_creation(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn('Accounts', tables)
        self.assertIn('Messages', tables)
        self.assertIn('Attachments', tables)
        self.assertIn('Threads', tables)
        conn.close()

    def test_fts_creation(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Messages_FTS'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

if __name__ == "__main__":
    unittest.main()
