# ArchyPEC

## Obiettivo
Creare un'applicazione desktop "Portable" per l'archiviazione intelligente, il ripristino dei messaggi e l'ottimizzazione automatica dello spazio su caselle PEC.

## Caratteristiche Principali

### 1. Interfaccia Utente (UI) e Design
- **Estetica Moderna**: UI pulita e minimale con supporto Dark/Light Mode.
- **Dashboard di Monitoraggio**: Grafico dello spazio occupato sul server PEC (IMAP QUOTA).
- **Vista a Thread**: Raggruppamento automatico di PEC inviate con ricevute di accettazione e consegna.

### 2. Gestione Archiviazione e Spazio (Core)
- **Archiviazione Automatica**: Download .eml e indicizzazione Full-Text (SQLite FTS5).
- **Auto-Pulizia (Retention Policy)**: Eliminazione dal server dei messaggi più vecchi di 6 mesi (se archiviati localmente).
- **Ripristino in Casella (Upload)**: Upload di .eml via IMAP APPEND.

### 3. Portabilità e Operatività
- **Zero Installazione**: Eseguibile da HDD/SSD esterno.
- **Lavoro in Background**: System tray integration.
- **Multi-Account**: Gestione simultanea di più indirizzi PEC.

### 4. Manutenzione e Utility
- **Esportazione PDF**: Conversione PEC e ricevute in PDF.
- **Backup Integrato**: Copia di sicurezza dell'intero archivio con un clic.
- **Accessibilità Dati**: File .eml non criptati per consultazione esterna.

## Struttura delle Cartelle
- `/app`: Risorse e codice.
- `/data`: Database SQLite (`archypec_main.db`).
- `/settings`: Configurazioni account.
- `/storage`: Archivio file .eml (organizzato per account/anno/mese).
- `/backups`: Copie di sicurezza.

## Tecnologia Suggerita
- **Linguaggio**: Python (PySide6).
- **Database**: SQLite.
- **Protocolli**: IMAP.
