# archivio — email/PEC archiver (MailStore-Home-like)

## Stack (DECISO, non proporre alternative)
- Python 3.12, FastAPI + Uvicorn, SQLite (stdlib sqlite3, FTS5).
- IMAP: imapclient. POP3: poplib. OAuth: authlib + httpx.
- Estrazione testo allegati: pypdf, python-docx, openpyxl, striprtf. NO Java/Tika.
- UI: Jinja2 + HTMX + Pico.css via CDN. NO npm, NO build step.
- Test: pytest. Config: pydantic-settings + config.json.

## Regole operative (token economy)
1. Esegui SOLO il task richiesto. Non anticipare i successivi.
2. Non stampare file interi: modifica in place, mostra solo i diff.
3. Test: `pytest -q`, mostra solo gli errori.
4. Un commit per task: `feat(scope): ...` / `fix(...)` / `test(...)`.
5. Niente docstring se non per logica non ovvia. Type hints sempre.
6. Max 200 righe per file. Se supera, splitta.
7. Cerca con `rg`, non con `cat`.
8. Non aggiungere dipendenze senza dichiararle in pyproject.toml.
9. Non riscrivere moduli esistenti: estendi.
10. A fine task: `pytest -q && git commit` e STOP.

## Layout
src/archivio/{config.py,db.py,models.py,storage.py,index.py,extract.py}
src/archivio/connectors/{base.py,imap.py,pop3.py,gmail.py,graph.py}
src/archivio/web/{app.py,routes.py,templates/,static/}
src/archivio/cli.py
tests/
migrations/0001_init.sql
data/archive/   # EML content-addressed: data/archive/ab/cd/<sha256>.eml

## Invarianti
- Messaggio grezzo SEMPRE salvato integrale (tutti gli header, incl. X-* PEC).
- Storage content-addressed: nome file = sha256(bytes EML). Dedup automatico.
- Archivio read-only sul server: mai inviare/scrivere/modificare via IMAP.
- Segreti cifrati a riposo (Fernet), mai in chiaro nel DB.
- Sync incrementale: (uidvalidity, last_uid) per cartella; se uidvalidity cambia → resync.
- Nessuna rete nei test: usa fixture .eml + fake IMAP.

## Comandi
make dev      # uvicorn src.archivio.web.app:app --reload --port 8765
make test     # pytest -q
make migrate  # applica migrations/*.sql in ordine
make lint     # ruff check + mypy