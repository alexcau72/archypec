PRAGMA journal_mode=WAL;
CREATE TABLE accounts(
  id INTEGER PRIMARY KEY, name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN('imap','pop3','gmail','graph')),
  host TEXT, port INTEGER, use_ssl INTEGER DEFAULT 1,
  username TEXT NOT NULL, secret_enc BLOB,
  created_at TEXT NOT NULL DEFAULT(datetime('now')));
CREATE TABLE folders(
  id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  remote_name TEXT NOT NULL, delim TEXT DEFAULT '/', special_use TEXT,
  uidvalidity INTEGER, last_uid INTEGER DEFAULT 0,
  UNIQUE(account_id, remote_name));
CREATE TABLE messages(
  id INTEGER PRIMARY KEY,
  folder_id INTEGER NOT NULL REFERENCES folders(id) ON DELETE CASCADE,
  uid INTEGER, message_id TEXT, sha256 TEXT NOT NULL, size INTEGER,
  date_utc TEXT, from_addr TEXT, to_addrs TEXT, cc_addrs TEXT, subject TEXT,
  has_attachments INTEGER DEFAULT 0, in_reply_to TEXT, refs TEXT,
  archived_at TEXT NOT NULL DEFAULT(datetime('now')),
  UNIQUE(folder_id, uid));
CREATE INDEX idx_msg_sha ON messages(sha256);
CREATE INDEX idx_msg_date ON messages(date_utc);
CREATE INDEX idx_msg_from ON messages(from_addr);
CREATE TABLE attachments(
  id INTEGER PRIMARY KEY,
  message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  filename TEXT, mime TEXT, size INTEGER, sha256 TEXT, text_extracted INTEGER DEFAULT 0);
CREATE VIRTUAL TABLE fts USING fts5(
  subject, from_addr, to_addrs, body, attachment_text,
  tokenize='unicode61 remove_diacritics 2');
CREATE TABLE tags(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);
CREATE TABLE message_tags(
  message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
  tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY(message_id, tag_id));
CREATE TABLE jobs(id INTEGER PRIMARY KEY, kind TEXT, payload TEXT, status TEXT,
  created_at TEXT, finished_at TEXT, error TEXT);