# TASKS — una fase per sessione, poi /clear

## P0 — Scheletro
- [ ] P0.1 pyproject.toml (deps sopra), Makefile, .gitignore, ruff+mypy config.
- [ ] P0.2 config.py: Settings (data_dir, db_path, fernet_key) da config.json + env.
- [ ] P0.3 db.py: connect() con WAL+foreign_keys, migrator che applica migrations/*.sql.
- [ ] P0.4 migrations/0001_init.sql (schema in schema.sql).
- [ ] P0.5 test_db.py: migrazione idempotente, tabelle presenti.
ACC: `make migrate && make test` verde.

## P1 — Storage
- [ ] P1.1 storage.py: put_eml(bytes)->sha256 (path ab/cd/hash.eml), get_eml(sha).
- [ ] P1.2 dedup: stesso contenuto → un solo file. Test con 2 identici.
- [ ] P1.3 parse.py: estrai header (from,to,cc,subject,date,message-id,in-reply-to,refs).
ACC: test_storage.py verde, nessun file duplicato.

## P2 — Connettore IMAP
- [ ] P2.1 connectors/base.py: Protocol Connector (list_folders, fetch_since).
- [ ] P2.2 connectors/imap.py: connect SSL, LIST, SELECT, UID SEARCH, fetch RFC822.
- [ ] P2.3 sync.py: per cartella leggi (uidvalidity,last_uid), scarica nuovi, aggiorna.
- [ ] P2.4 CLI `archivio add-account` e `archivio sync <id>`.
ACC: test_imap.py con fake server; sync reale su casella demo produce righe in messages.

## P3 — Indice
- [ ] P3.1 extract.py: testo da pdf/docx/xlsx/rtf/plain; fallback bytes→utf8.
- [ ] P3.2 index.py: insert/delete su fts(rowid=message.id); rebuild().
- [ ] P3.3 hook in sync: dopo insert messaggio → indicizza + allega.
ACC: ricerca "fattura" trova messaggio e testo allegato.

## P4 — UI
- [ ] P4.1 web/app.py + routes: GET / (lista), GET /search?q= (FTS + filtri data/mittente/allegati).
- [ ] P4.2 templates con HTMX: ricerca live, paginazione, anteprima messaggio.
- [ ] P4.3 GET /message/{id}: rendi header + body, lista allegati scaricabili.
ACC: `make dev`, cerchi e apri un messaggio dal browser.

## P5 — Export
- [ ] P5.1 export EML singolo e ZIP di selezione.
- [ ] P5.2 export mbox per cartella.
- [ ] P5.3 re-upload su IMAP di destinazione (APPEND), idempotente per Message-ID.
ACC: export→reimport produce lo stesso conteggio.

## P6 — OAuth (Gmail/Graph)
- [ ] P6.1 authlib flow locale (redirect 127.0.0.1), token in DB cifrato.
- [ ] P6.2 connectors/gmail.py (users.messages.list/get, format=raw).
- [ ] P6.3 connectors/graph.py (mailFolders, messages/$value).
ACC: archiviare una casella Gmail di prova.

## P7 — Scheduler + rifinitura
- [ ] P7.1 job periodici (APScheduler) + tabella jobs.
- [ ] P7.2 POP3 connector.
- [ ] P7.3 gestione errori/report sync, log strutturato.
ACC: sync automatico ogni N minuti, errori visibili in UI.

## P8 — Consegna
- [ ] P8.1 PyInstaller one-folder, avvio server locale + apre browser.
- [ ] P8.2 README + screenshot.
ACC: eseguibile su Windows pulito archivia una casella IMAP.