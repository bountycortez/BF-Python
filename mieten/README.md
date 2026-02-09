# Mietbuchungen Analyse

Automatisierte Analyse und Kategorisierung von Buchungen auf dem Vermietungskonto mit intelligenter Objekt- und Partnerzuordnung.

## Überblick

Dieses Projekt analysiert Banktransaktionen eines Vermietungskontos und kategorisiert sie automatisch nach Buchungstyp (Miete, Betriebskosten, Kaution, etc.) sowie nach Mietobjekten (OBIDs). Das Script erstellt detaillierte Analysen und Zusammenfassungen für Buchhaltung und Steuererklärung.

**Version:** 2026-02-09 15:00:00

## Features

### Intelligente Buchungstyp-Erkennung

**13 Buchungstypen werden automatisch erkannt:**
- Miete
- Betriebskosten
- Rücküberweisung
- Kaution
- Energiekosten
- Reparatur
- Eigenentnahme
- Steuer
- Beratung
- Spende
- Versorgung
- Kostenersatz
- Abschluss
- Sonstiges

**Automatische Kategorisierung durch mehrstufiges System:**
1. **Partnertyp-Analyse**: Prüfung des Partnertyps aus partner.csv (z.B. Mieter, Hausverwaltung, Energieversorger)
2. **Textanalyse**: Durchsuchen von 6 kombinierten Feldern nach Schlüsselwörtern
3. **Betragsrichtung**: Bei Hausverwaltung entscheidet das Vorzeichen (positiv/negativ)
4. **Kontext-Regeln**: Zusätzliche Logik wie TopNummer-Erkennung, HVID-Matching
5. **Fallback-Logik**: Intelligente Standardwerte wenn eindeutig zuordenbar

**Erweiterte Textsuche über 6 Felder:**
- Buchungstext
- Umsatztext
- Verwendungszweck
- Name des Partners
- Zahlungsreferenz
- Auftraggeberreferenz

Alle 6 Felder werden kombiniert durchsucht nach OBID, HVID, EVID sowie nach Schlüsselwörtern wie "Miete", "Betriebskosten", "Kaution", etc.

### Objektzuordnung
- ✓ **OBID-Erkennung** (Objekt-ID) aus Buchungstext
- ✓ **HVID-Erkennung** (Hausverwaltungs-ID) mit Wortgrenzen-Matching
- ✓ **EVID-Erkennung** (Energieversorger-ID)
- ✓ **Fuzzy-Matching** für flexible OBID-Suche (z.B. "h2640" findet "H26T40")
- ✓ **Fallback-Regeln** bei eindeutiger Zuordnung

### Spezielle Logiken
- ✓ **Hausverwaltung**: Positive Beträge = Rücküberweisung, negative = Betriebskosten
- ✓ **Kaution**: Intelligente Zuordnung über Mieternamen-Suche
- ✓ **Mieter mit Wohnung+Garage**: Automatische Größen-basierte Zuordnung
- ✓ **IBAN-Validierung** mit Prüfsummen-Check

### Summary-Berichte
- ✓ **Monatliche Auswertungen** nach Buchungstyp, OBID, Partner
- ✓ **Total-Übersichten** über alle Zeiträume
- ✓ **Partner-IBAN (Partnername)** Format für bessere Lesbarkeit
- ✓ **Saldo-Berechnungen** mit positiven/negativen Summen getrennt

### Monatliche Wohneinheiten-Übersicht
- ✓ **out_JJJJMM.txt** — Fixed-Width-Tabelle pro Monat, jede OBID eine eigene Zeile
- ✓ **out_JJJJMM.md** — Markdown-Tabelle pro Monat (gleicher Inhalt)
- ✓ Spalten: OBID, Mietername, Miete, BKMi, BKHV, Diag, Reparatur, Energie
- ✓ Jede Garage bekommt eine eigene Zeile (nicht mehr in Wohnungszeile eingefaltet)
- ✓ Garagen werden nach ihrer zugehörigen Wohnung sortiert, verwaiste Garagen am Ende
- ✓ BK aufgetrennt nach Quelle: Mieter (Eingang) vs Hausverwaltung (Ausgang, netto inkl. Rücküberweisungen)
- ✓ **Energie**: Energiekosten (z.B. IKB) pro Objekt
- ✓ **Diagnose-Spalte**: W/G (w/g bei Eigennutzung) + <, >, = für BKMi vs |BKHV|
- ✓ **Primärer Mieter** wird über Mietzahlungen erkannt (nicht über partner.csv-Reihenfolge)
- ✓ SUMME-Zeile mit Spaltensummen
- ✓ **Reparaturen**: Detailauflistung unter der Tabelle (Datum, OBID, Betrieb, Betrag, Beschreibung)
- ✓ **Kautionen**: Zusammenfassung pro OBID (Mieter-Name, Betrag von/an Mieter, Vermieter-Betrag)
- ✓ **Eigenentnahmen**: Datum, Betrag, Empfängerkonto

### Plausibilitätsprüfung (NEU)
- ✓ **Mietpreis-Schwankungen** >5% zum Vormonat
- ✓ **Doppelzahlungen** erkennen (gleicher Mieter/Betrag/Monat/OBID)
- ✓ **Unkategorisierte Buchungen** melden (Typ "Sonstiges")
- ✓ **Hohe Einzelbeträge** >5000 EUR (außer Kaution)

### Excel-Output (NEU)
- ✓ **out_mieten.xlsx** mit Sheets: Analyse, Summary, Monatsübersicht, Plausibilität
- ✓ Farbcodierte Beträge (grün/rot), formatierte Header, Auto-Spaltenbreite

## Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Setup

```bash
# 1. Virtual Environment erstellen
python3 -m venv venv

# 2. Environment aktivieren
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# 3. Abhängigkeiten installieren
pip3 install pandas
```

## Verwendung

### 1. Input-Dateien vorbereiten

**partner.csv** (Konfiguration)
- Enthält alle Buchungspartner (Bank, Vermieter, Mieter, Hausverwaltung, etc.)
- Definiert Mietobjekte mit OBID, HVID, EVID
- Format: UTF-8, Semikolon-Separator, LF Line-Terminators
- Kommentarzeilen mit `#` am Anfang werden ignoriert

**umsaetze.csv** (Bank-Export)
- CSV-Export vom Bankkonto mit allen Transaktionen
- Format: ISO-8859, Semikolon-Separator, CRLF Line-Terminators
- Felder: Valutadatum, Buchungstext, Verwendungszweck, Betrag, Kontoverbindung des Partners, etc.

### 2. Analyse durchführen

```bash
# Environment aktivieren (falls noch nicht aktiv)
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Analyse starten
python3 analyse.py
```

### 3. Environment deaktivieren (optional)

Nach der Analyse kann das Virtual Environment wieder deaktiviert werden:

```bash
deactivate
```

### 4. Output-Dateien

**out_analyse.csv**
- Detaillierte Analyse aller Buchungen
- Felder: Valutadatum, Buchungstyp, Objekttyp, OBID, HVID, EVID, Partner-IBAN, Partnername, Betrag, Kommentar
- Format: UTF-8, Semikolon-Separator, LF Line-Terminators

**out_summary.csv**
- Zusammenfassungen gruppiert nach verschiedenen Dimensionen
- Felder: Titel, Dimension, Gruppierung1, Gruppierung2, Saldo, SummePositiveBeträge, SummeNegativeBeträge, AnzahlBuchungen
- 6 verschiedene Gruppierungen für umfassende Auswertungen

**out_JJJJMM.txt** und **out_JJJJMM.md** (pro Monat)
- Tabellarische Wohneinheiten-Übersicht, jede OBID (Wohnung und Garage) eine eigene Zeile
- Spalten: OBID, Mietername, Miete, BKMi, BKHV, Diag, Reparatur, Energie
- Diag: W/G (w/g bei Eigennutzung) + <, >, = (z.B. "W =" oder "g <")
- Nach der Tabelle: Reparaturen, Kautionen, Eigenentnahmen (falls vorhanden)
- .txt: Fixed-Width mit rechtsbündigen Beträgen, .md: Markdown-Tabelle
- SUMME-Zeile am Ende

**out_mieten.xlsx**
- Excel-Datei mit Sheets: Analyse, Summary, Monatsübersicht, Plausibilität
- Formatierte Header, farbcodierte Beträge, Auto-Spaltenbreite

## Buchungstypen im Detail

Die automatische Kategorisierung erfolgt nach folgenden Regeln:

### 1. Miete
- **Partnertyp**: Mieter oder Vermieter
- **Erkennungskriterium**: Text "Miete" (auch kleingeschrieben) muss im Buchungstext vorkommen
- **Objektzuordnung**: Ja, über OBID oder TopNummer im Text
- **Besonderheit**: TopNummer (z.B. "T34" aus "H26T34") wird bevorzugt erkannt

### 2. Betriebskosten
- **Partnertyp**: Mieter, Vermieter oder Hausverwaltung
- **Erkennungskriterium**:
  - Schlüsselwörter: "Betriebskosten", "BK", "Vorschreibung", "Vorschr.", "Nebenkosten"
  - Bei Hausverwaltung: Negativer Betrag (Abgang)
- **Objektzuordnung**: Ja, über OBID/HVID
- **Besonderheit**: Bei Hausverwaltung muss HVID im Text gefunden werden

### 3. Rücküberweisung
- **Partnertyp**: Hausverwaltung
- **Erkennungskriterium**: Positiver Betrag (Eingang von Hausverwaltung)
- **Objektzuordnung**: Ja, über HVID im Text
- **Besonderheit**: Neu seit Version 2026-02-03, trennt Rückzahlungen von Betriebskosten

### 4. Kaution
- **Partnertyp**: Mieter oder Vermieter
- **Erkennungskriterium**: Text "Kaution" muss vorkommen
- **Objektzuordnung**: Ja, über OBID oder Mietername-Suche
- **Besonderheit**: Bei Vermieter wird zuerst nach Mietername gesucht, dessen Wohnung wird zugeordnet

### 5. Energiekosten
- **Partnertyp**: Energieversorger
- **Erkennungskriterium**: Automatisch durch Partnertyp
- **Objektzuordnung**: Ja, über EVID (Energieversorger-ID) im Text
- **Besonderheit**: Warnung wenn EVID nicht gefunden werden kann

### 6. Reparatur
- **Partnertyp**: Handwerker
- **Erkennungskriterium**: Automatisch durch Partnertyp
- **Objektzuordnung**: Ja, über OBID im Text
- **Besonderheit**: Warnung bei fehlender Objektzuordnung

### 7. Eigenentnahme
- **Partnertyp**: Vermieter
- **Erkennungskriterium**: Automatisch, aber Text "Kaution" darf nicht vorkommen
- **Objektzuordnung**: Nein
- **Besonderheit**: Für private Entnahmen des Vermieters

### 8. Steuer
- **Partnertyp**: Finanzamt
- **Erkennungskriterium**: Automatisch durch Partnertyp
- **Objektzuordnung**: Nein

### 9. Beratung
- **Partnertyp**: Beratung (Steuerberater, Rechtsanwalt, etc.)
- **Erkennungskriterium**: Automatisch durch Partnertyp
- **Objektzuordnung**: Nein

### 10. Spende
- **Partnertyp**: Spende
- **Erkennungskriterium**: Automatisch durch Partnertyp
- **Objektzuordnung**: Nein

### 11. Versorgung
- **Partnertyp**: Versorgung
- **Erkennungskriterium**: Automatisch durch Partnertyp
- **Objektzuordnung**: Nein
- **Besonderheit**: Für wiederkehrende Zahlungen (z.B. Hausmeister, Reinigung)

### 12. Kostenersatz
- **Partnertyp**: Mieter
- **Erkennungskriterium**: Text "Kostenersatz" im Buchungstext
- **Objektzuordnung**: Ja, über OBID im Text
- **Besonderheit**: Für Rückerstattungen an Mieter (z.B. zu viel gezahlte Nebenkosten)

### 13. Abschluss
- **Partnertyp**: Bank
- **Erkennungskriterium**: Text "Abschluss" im Buchungstext
- **Objektzuordnung**: Nein
- **Besonderheit**: Bankinterne Buchungen (Kontoführung, Zinsen, etc.)

### 14. Sonstiges
- **Partnertyp**: Beliebig
- **Erkennungskriterium**: Fallback wenn keine andere Kategorie zutrifft
- **Objektzuordnung**: Abhängig vom Partnertyp

## Automatische Kategorisierung - Der Prozess

Das Script kategorisiert jede Buchung durch einen mehrstufigen Analyseprozess:

### Phase 1: Partner-Identifikation
1. **IBAN-Lookup**: Partner-IBAN aus Buchung wird in partner.csv nachgeschlagen
2. **Partnertyp-Bestimmung**: Typ des Partners wird ermittelt (z.B. "Mieter", "Hausverwaltung")
3. **IBAN-Validierung**: Prüfsumme wird geprüft, Warnung bei ungültiger IBAN

### Phase 2: Textanalyse
1. **Feld-Kombination**: 6 Felder werden zu einem Suchtext kombiniert
2. **Normalisierung**: Text wird in Kleinbuchstaben umgewandelt
3. **Schlüsselwort-Suche**: Suche nach Schlüsselwörtern wie "Miete", "BK", "Kaution"
4. **ID-Extraktion**: Suche nach OBID, HVID, EVID im kombinierten Text

### Phase 3: Buchungstyp-Ermittlung
```
IF Partnertyp = "Energieversorger"
  → Buchungstyp = "Energiekosten"

ELSE IF Partnertyp = "Hausverwaltung"
  IF Betrag > 0
    → Buchungstyp = "Rücküberweisung"
  ELSE
    → Buchungstyp = "Betriebskosten"

ELSE IF Partnertyp = "Mieter"
  IF Text enthält "Kaution"
    → Buchungstyp = "Kaution"
  ELSE IF Text enthält "Miete"
    → Buchungstyp = "Miete"
  ELSE IF Text enthält BK-Schlüsselwörter
    → Buchungstyp = "Betriebskosten"
  ELSE
    IF TopNummer gefunden
      → Buchungstyp = "Miete"
    ELSE IF HVID gefunden
      → Buchungstyp = "Betriebskosten"
    ELSE
      → Buchungstyp = "Betriebskosten" (Fallback)
```

### Phase 4: Objektzuordnung (wenn erforderlich)
1. **Direkte OBID-Suche**: Vollständige OBID im Text (z.B. "H26T40")
2. **HVID-Suche**: Mit Wortgrenzen-Matching (z.B. "/4001", "4001/")
3. **TopNummer-Suche**: Suffix der OBID (z.B. "T40" aus "H26T40")
4. **Nur-Nummer-Suche**: Nur die Endziffer (z.B. "40", mindestens 2 Ziffern)
5. **Fuzzy-Matching**: Zerlegung in Prefix + Nummer (z.B. "h26" + "40")
6. **Fallback bei Eindeutigkeit**: Wenn Mieter nur 1 Wohnung hat

### Phase 5: Spezielle Logiken
- **Wohnung+Garage**: Größerer Betrag → Wohnung, kleinerer → Garage
- **Kaution-Vermieter**: Mietername-Suche im Text, Zuordnung zu dessen Wohnung
- **HVID-Priorität**: Längere HVIDs werden zuerst geprüft (verhindert "3401" statt "4001")

### Phase 6: Validierung & Warnungen
- **IBAN-Prüfung**: Warnung bei fehlender oder ungültiger IBAN
- **Objektzuordnung**: Warnung wenn erforderlich aber nicht gefunden
- **OBID-Widerspruch**: Warnung bei Kaution wenn Text-OBID ≠ Mieter-OBID
- **Währung**: Warnung und Ignorieren bei Nicht-EUR Buchungen

## Intelligente Features

### Fuzzy-OBID-Suche
Findet OBID auch bei ungenauen Schreibweisen:
- "h2640" findet "H26T40" (Prefix "h26" + Nummer "40")
- "26 40" findet "H26T40" (nur Zahlen)
- "t34" findet "H26T34" (TopNummer)

### Automatische Wohnung/Garage-Zuordnung
Wenn ein Mieter Wohnung + Garage hat und 2 Buchungen im selben Monat:
- Größerer Betrag → Wohnung
- Kleinerer Betrag → Garage

### Kaution-Zuordnung bei Vermieter
Bei Kautions-Buchungen vom Vermieter:
1. Suche Mietername im Text
2. Verwende Wohnung dieses Mieters
3. Warnung bei OBID-Widersprüchen

### HVID-Matching mit Wortgrenzen
Verhindert falsche Matches (z.B. "3401" statt "4001"):
- Sucht nach `/4001`, `4001/`, `-4001`, `4001-`
- Sortiert nach HVID-Länge (längste zuerst)
- Prüft zuerst vollständige OBID

## Summary-Gruppierungen

Die Summary-Datei enthält 6 verschiedene Auswertungen:

1. **Monat/Buchungstyp/OBID**: Welche Buchungstypen pro Objekt und Monat
2. **Monat/Buchungstyp/IBAN**: Welche Buchungstypen pro Partner und Monat
3. **Monat/OBID/Objekttyp**: Einnahmen/Ausgaben pro Objekt und Monat
4. **Monat/OBID**: Gesamt pro Objekt und Monat
5. **Monat/IBAN/Objekttyp**: Partner-Aktivität nach Objekttyp
6. **Total/IBAN**: Gesamt-Übersicht pro Partner

## Warnungen und Validierung

Das Script gibt Warnungen aus bei:
- ✓ Fehlenden oder ungültigen IBANs
- ✓ Buchungen ohne Objektzuordnung (wenn erforderlich)
- ✓ OBID-Widersprüchen bei Kaution
- ✓ Nicht-EUR Währungen
- ✓ Fehlenden Partner-IBANs

Format der Warnungen:
```
WARNUNG (umsaetze.csv, Zeile 15, 2026-01-15): OBID H26T34 im Text gefunden, aber Mieter gehört zu H26T36. Verwende H26T36.
```

## Spezifikation

Die vollständige Spezifikation befindet sich als Kommentar im Script `analyse.py` (Zeilen 1-145).

Dort dokumentiert:
- Alle Input/Output-Formate
- Buchungstyp-Regeln im Detail
- Objektzuordnungs-Logik
- Fuzzy-Suche Algorithmus
- Fallback-Regeln
- Summary-Gruppierungen

## Beispiel-Output

**out_analyse.csv:**
```csv
Valutadatum;Buchungstyp;Objekttyp;OBID;HVID;EVID;Partner-IBAN;Partnername;Betrag;Kommentar
2026-02-02;Miete;Wohnung;H26T41;4101;;AT441600000407066847;Helga KIRCHLER;605.00;einkünftepssaat...
2026-02-02;Betriebskosten;Wohnung;H26T41;4101;;AT441600000407066847;Helga KIRCHLER;182.43;wohnen&haushalt...
2026-01-08;Rücküberweisung;Wohnung;H26T38;3801;;AT072051000000042275;HIM GesmbH / WEG H26;169.72;2-3801/rücküberweisung...
```

**out_summary.csv:**
```csv
Titel;Dimension;Gruppierung1;Gruppierung2;Saldo;SummePositiveBeträge;SummeNegativeBeträge;AnzahlBuchungen
Monat/Buchungstyp/OBID;2026-02;Miete;H26T41;605.00;605.00;0.00;1
Monat/IBAN/Objekttyp;2026-02;AT441600000407066847 (Helga KIRCHLER);Wohnung;787.43;787.43;0.00;2
Total/IBAN;Total;AT441600000407066847 (Helga KIRCHLER);keine;2355.86;2355.86;0.00;6
```

## Technische Details

- **Sprache**: Python 3
- **Framework**: pandas für CSV-Verarbeitung
- **Encoding**: Input ISO-8859-1, Output UTF-8
- **Line Terminators**: Input CRLF, Output LF
- **Betragsformat**: Deutsches Format (1.234,56 → 1234.56)
- **Datumsformat**: ISO 8601 (YYYY-MM-DD)

## Dateistruktur

```
.
├── analyse.py          # Haupt-Script mit vollständiger Spezifikation
├── partner.csv         # Konfiguration (Partner, Objekte, IDs)
├── umsaetze.csv        # Input: Bank-Export
├── out_analyse.csv     # Output: Detaillierte Analyse
├── out_summary.csv     # Output: Zusammenfassungen
├── out_JJJJMM.txt     # Output: Monatliche Wohneinheiten-Übersicht (Text)
├── out_JJJJMM.md      # Output: Monatliche Wohneinheiten-Übersicht (Markdown)
├── out_mieten.xlsx     # Output: Excel mit allen Sheets
└── README.md           # Diese Datei
```

## Changelog

### Version 2026-02-09 09:00:00
- ✓ Monatliche Wohneinheiten-Übersicht: jede OBID (Wohnung + Garage) eigene Zeile
- ✓ Spalten vereinfacht: Miete, BKMi, BKHV, Reparatur, Energie, Diag
- ✓ BKHV netto inkl. Rücküberweisungen der HV
- ✓ Energiekosten als eigene Spalte pro Objekt
- ✓ Neuer Output: Excel-Datei (out_mieten.xlsx) mit 4 Sheets
- ✓ Diagnose-Spalte: W/G + <, >, = für BKMi vs |BKHV| Vergleich
- ✓ Primärer Mieter wird über tatsächliche Mietzahlungen erkannt
- ✓ Plausibilitätsprüfung (Mietpreis-Schwankungen, Doppelzahlungen, Anomalien)
- ✓ Monats-Vollständigkeitsprüfung (fehlende Miete/BK pro Objekt)
- ✓ Bugfix: Berater/Beratung Partnertyp-Mismatch
- ✓ Bugfix: IBAN-Kollision bei Eigennutzung (Vermieter = Mieter)

### Version 2026-02-03 19:01:00
- ✓ README.md umfassend überarbeitet
- ✓ Spezifikation aktualisiert und Tippfehler korrigiert
- ✓ Partner-IBAN (Partnername) Format in Summary
- ✓ Neuer Buchungstyp "Rücküberweisung" für Hausverwaltung
- ✓ Erweiterte Suchfelder (Zahlungsreferenz)
- ✓ Verbesserte HVID-Suche mit Wortgrenzen
- ✓ Alle Tippfehler in Spezifikation korrigiert

## Autor

Bernd Flunger (bernd.flunger@gmail.com)

## Lizenz

Privates Projekt für persönliche Vermietungsverwaltung
