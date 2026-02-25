# XMENU
## a graphical interface for commands in ttkbootstrap

Start commands defined in `xmenu.json` from buttons and see their output in a scrollable textbox.

Originally based on customtkinter, migrated to ttkbootstrap.

---

## Installation

```bash
pip install -r requirements.txt
python xmenu.py --cmdfiledir .
```

---

## xmenu.json Format

```json
{
  "version": "1.0",
  "menuitems": [
    { "cmdname": "MyCmd", "cmd": "echo hello", "cmdoutput": true }
  ]
}
```

---

## Security

### CVE-2025-47287 (urllib3 < 2.4.0)
**Decompression-bomb safeguards bypassed when following HTTP redirects (streaming API)**

- Fixed by pinning `urllib3>=2.4.0` in `requirements.txt`
- Current tested version: 2.6.3

---

## Verbesserungsvorschläge (offen)

| # | Thema | Beschreibung |
|---|-------|-------------|
| 1 | `cmdoutput=false`-Branch | Derzeit: stdout verworfen, nur stderr im Textbox. Ggf. beides zusammenführen (wie `cmdoutput=true`) oder Flag umbenennen in `show_stdout`/`show_stderr` für Klarheit |
| 2 | JSON-Schema-Validierung | `xmenu.json` wird ohne Validierung geladen – bei fehlenden Feldern gibt es kryptische Fehler. Empfehlung: `jsonschema`-Library einsetzen |
| 3 | Typen-Annotationen | Die meisten Methoden haben keine Return-Type-Hints; konsistenter Einsatz von `-> bool`, `-> None` etc. verbessert Lesbarkeit |
| 4 | Konfiguration via `.env` / CLI | Pfade zu JSON/Logdir aktuell nur über CLI-Argumente – ein `.env`-File (mit `python-dotenv`) wäre nutzerfreundlicher |
| 5 | Unit-Tests | Kein Test-Framework vorhanden; zumindest `load_commands()` und Argument-Parsing sollten getestet werden (`pytest`) |
| 6 | `destroy()` Deadlock | `while True: if process_queues()==0: break` kann hängen, wenn ein laufender Thread dauerhaft neue Items in die Queue stellt |

---

## Changelog

| Version | Datum | Änderung |
|---------|-------|----------|
| 20230408-000000 | 2023-04-08 | Initial release (Athena) |
| 20260225-000000 | 2026-02-25 | Helios: requirements.txt (CVE-2025-47287), Timestamp-Fix, IntVar-Fix, shell=False, except Exception, Lock-Timing, Retval-Fix |
