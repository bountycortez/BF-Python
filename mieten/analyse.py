"""
#Script analyse.py Version 2026-02-09 15:00:00

Sinn des Scriptes: ANALYSE und SUMMARY der MIETBUCHUNGEN von BF

SPEZIFIKATION
0) Version oben im Script immer auf JJJJ-MM-DD hh:mi:ss setzen
1) INPUT partner.csv: 
   - Manuell erstelle Konfigurations-Datei für die Buchungspartner sowie für die Mietobjekte/Wohneinheiten
   - CSV mit Separator=;, 1. Zeile = Header, UTF-8, nur LF line terminators
   - Zeilen mit '#' als erstem Zeichen in der ersten Spalte bzw. am Zeilenanfang sowie Leerzeilen sind zu ignorieren
   - Ein leeres Feld (;;) bedeutet ein leeres Feld (leerer String).
   - Mögliche Partnertypen: Bank|Vermieter|Mieter|Hausverwaltung|Energieversorger|Handwerker|Finanzamt|Beratung|Spende|Versorgung|Sonstige
   - Partnername: Bezeichnung des Buchungspartners
   - Partner-IBAN: IBAN und eindeutiger Partner-Key, damit kann jeder Buchung ein Partner zugeordnet werden
     Bank ist ein spezieller Partner/Partnertyp, der keine gültige Partner-IBAN benötigt und nur einmal vorkommen darf.
     Gib ein Warnung aus, wenn ein IBAN fehlt (ausser bei Bank) oder die IBAN Prüfsumme nicht korrekt ist.
   - Mietobjekte/Wohneinheiten werden implizit beim Partnertyp Mieter mitdefiniert
     > OBID: eindeutige Vermieter ID des Mietobjektes bzw. der Wohneinheit
     > HVID: eindeutige Hausverwaltungs ID des Mietobjektes bzw. der Wohneinheit (entspricht genau einer OBID)
     > EVID: eindeutige Energieversorger ID des Mietobjektse bzw. der Wohnungseinheit
     > Objekttyp: Art des Mietobjektes, kann nur Wohnung oder Garage sein
   - Den Mietobjekten/Wohneinheiten sind mögliche Mieter zugeordnet.
   - Den Mietern sind mögliche Mietobjekte/Wohneinheiten zugeordnet.
   - Es muss eine Partnertable mit dem Partner-IBAN als eindeutigem Key aufgebaut werden.
   - Es muss eine OBID->HVID,EVID-Table mit der OBID als eindeutigem Key aufgebaut werden.
   - Es muss eine HVID->OBID-Table mit der HVID als eindeutigem Key aufgebaut werden.
   - Es muss eine EVID->OBID-Table mit der EVID als eindeutigem Key aufgebaut werden.
   - Es muss für Mietertable mit dem nicht eindeutigen Partner-IBAN und den möglichen OBIDs aufgebaut werden.
     Diese Table schränkt für Mieter die möglichen OBID/HVID/EVID ein.
   - Es muss eine Wohneinheiten-Table mit der OBID als nicht eindeutigem KEY und den möglichen Partner-IBAN aufgebaut werden.
     Diese Table schränkt für Wohneinheiten (also eine OBID/HVID/EVID) die möglichen Partner-IBAN ein.
   - Bei allen Warnungen (zB IBAN nicht korrekt) muss die Zeilennummer in partner.csv ausgegeben werden.
2) INPUT umsaetze.csv: 
   - Umsatzdaten/Buchungen der Bank betreffend Vermietung direkt vom Vermieter Mietenkonto (CSV-Export) die analysiert werden sollen
   - CSV mit Separator ;, 1. Zeile = Header, ISO-8859 text, with very long lines (750), with CRLF line terminators
   - Buchungszeilen mit Text 'Verständigung' im Feld Buchungstext sind zu ignorieren.
   - Das Buchungsdatum steht im Feld Valutadatum, Datum wird im Format YYYY-MM-DD aus den Feld eingelesen (ISO-Standard).
   - Der Buchungstext im Feld Buchungstext
   - Der Verwendungszweck im Feld Verwendungszweck
   - Im Feld Waehrung steht die Waehrung, das sollten nur EUR sein.
   - Im Feld Betrag steht negativ ein Abgang aus dem Konto und positiv ein Zugang, die Werte sind Deutsch formatiert
     (. für die Tausenderstelle und , für die Kommastelle), Beträge immer mit 2 fixen Kommastellen behandeln, es geht um EURO.
     Gib eine Warnung aus, wenn die Waehrung nicht EUR ist und ignoriere diese Zeile.
   - Der Partner-IBAN zur Buchungsteht im Feld 'Kontoverbindung des Partners'
   - Bei Buchungstext Abschluss ist keine Partner-IBAN angegeben, ordne hier statt einem IBAN den Wert NOIBAN und Partnername BANK als Partner zu.
     Gib eine Warnung aus, wenn eine Buchungszeile ohne Partner-IBAN auftaucht, ausser der Buchungstext ist Verständigung.
   - Für die Buchungstyp-Erkennung und Objektzuordnung werden folgende Felder analysiert:
     Buchungstext, Umsatztext, Verwendungszweck, Name des Partners, Zahlungsreferenz, Auftraggeberreferenz
     Diese Felder werden kombiniert durchsucht nach OBID, HVID, EVID sowie nach Schlüsselwörtern wie 'Miete', 'Betriebskosten', 'Kaution', etc.
8) OUTPUT out_analyse.csv:
   - Die erste von diesem Analyse-Script erstellte Datei, die die Buchungen in umsaetze.csv aufbereitet
   - CSV mit Separator=;, 1. Zeile = Header, UTF-8, nur LF line terminators
   - Felder: Valutadatum;Buchungstyp;Objekttyp;OBID;HVID;EVID;Partner-IBAN;Partnername;Betrag;Kommentar
   - Der Buchungstyp einer Buchung ergibt sich aus dem Partner und der Analyse der Umsatztexte bzw. aller Texte in der Buchungszeile
   - Mögliche Buchungstypen: Abschluss|Energiekosten|Steuer|Beratung|Spende|Versorgung|Eigenentnahme|Reparatur|Kostenersatz|Kaution|Miete|Betriebskosten|Rücküberweisung|Sonstiges
     > Buchungstyp Abschluss: Liegt vor, wenn im Feld Buchungstext 'Abschluss' steht. 
       Hier ist die Bank als Partner zuzuordnen, da das Partner-IBAN Feld leer ist.
       Es gibt keine OBID/HVID/EVID-Zuordnung.
     > Buchungstyp Energiekosten: Partner muss ein Energieversorger sein, die OBID + HVID kann über die EVID zugeordnet werden,
       die in der Buchungszeile vorkommen muss. Ansonsten Warnung bei Energieversorger-Buchungen ausgeben.
     > Buchungstyp Steuer: Partner muss ein Finanzamt sein, es gibt keine OBID/HVID/EVID-Zuordnung.
     > Buchungstyp Beratung: Partner muss ein Berater sein, es gibt keine OBID/HVID/EVID-Zuordnung.
     > Buchungstyp Spende: Partner muss vom Typ Spende sein, es gibt keine OBID/HVID/EVID-Zuordnung.
     > Buchungstyp Versorgung: Partner muss vom Typ Versorgung sein, es gibt keine OBID/HVID/EVID-Zuordnung.
     > Buchungstyp Eigenentnahme: Partner muss vom Typ Vermieter sein, es gibt keine OBID/HVID/EVID-Zuordnung.
       In der Buchungszeile darf der Text 'Kaution' nicht vorkommen.
     > Buchungstyp Reparatur: Partner muss vom Typ Handwerker sein, es muss über die Buchungszeile eine Zuordnung zur OBID hergestellt werden.
       Warnung, wenn die Objektzuordnung nicht gelingt.
     > Buchungstyp Kostenersatz: Partner muss vom Typ Mieter sein, es muss über die Buchungszeile eine Zuordnung zur OBID hergestellt werden.
       Warnung, wenn die Objektzuordnung nicht gelingt.
     > Buchungstyp Kaution: Partner muss ein Mieter oder Vermieter sein.
       In der Buchungszeile muss der Text 'Kaution' vorkommen und es muss eine Zuordnung zur OBID hergestellt werden.
       Die OBID muss dabei nicht im Text der Buchungszeile gefunden werden.
       Es muss dann aber eindeutig einer OBID zuordenbar sein. Werden eine Wohnung und eine Garage gefunden, dann wird der Wohnung zugeordnet.
       Bei Kaution vom Vermieter: Suche nach einem Mieternamen im Text. Wenn gefunden, verwende die Wohnung dieses Mieters.
       Wenn die im Text gefundene OBID nicht zur Wohnung des im Text genannten Mieters passt → Warnung und korrekte OBID verwenden.
       Warnung, wenn die Objektzuordnung nicht gelingt.
     > Buchungstyp Miete: Partner muss ein Mieter oder Vermieter sein.
       Nur wenn in der Buchungszeile der Text 'Miete' (auch kleingeschrieben) vorkommt, dann ist der Buchungstyp Miete.
       Beim Buchungstyp Mieter ergeben sich die möglichen OBID aus partner.csv.
       Die OBID oder nur die Zahl am Ende der OBID nach dem letzten Buchstaben muss in der Buchungszeile gefunden werden.
       Fallback 1: Wenn keine Zuordnung zu einem Mietobjekt gelingt, weil keine OBID im Verwendungszweck enthalten ist,
       der Mieter aber genau eine Wohneinheit zugeordnet hat, dann ist diese Zuornung anzunehmen.
       Fallback 2: Würde im selben Monat bei einem konkreten Mieter die Objektzuordnung 2 mal gefunden, dann ist der grössere Betrag dem Objekttyp Wohnung
       und der kleinere Betrag dem Objekttyp Garage zuzuordnen.
       Warnung, wenn die Objektzuordnung nicht gelingt.
       Warnung, wenn in einem Monat ein Objekt keine Zuordnung eines Mietbetrags bekommen hat.
     > Buchungstyp Betriebskosten: Partner muss ein Mieter oder Vermieter oder eine Hausverwaltung sein.
       Beim Partner Hausverwaltung mit negativem Betrag (Abgang) muss in der Buchungszeile die HVID im Verwendungszweck gefunden werden, die die OBJID-Zuordnung eindeutig macht.
       Beim Partner Hausverwaltung mit positivem Betrag (Eingang) ist der Buchungstyp Rücküberweisung (nicht Betriebskosten).
       Kommt in der Buchungszeile der Text 'Miete' (egal ob groß- oder Kleinbuchstaben) vor, dann ist es eine Miete und keine Betriebskosten.
       Ansonsten zeigen die Texte 'Betriebskosten', 'BK', 'Vorschreibung', 'Vorschr.', 'Nebenkosten' in der Buchungszeile eindeutig den Buchungstyp Betriebskosten an.
       Beim Partner Vermieter muss die OBID oder die HVID in der Buchungszeile im Verwendungszweck gefunden werden.
       Beim Partner Mieter muss die OBID oder HVID oder nur die Zahl am Ende der OBID nach dem letzten Buchstaben 
       in der Buchungszeile im Verwendungszweck gefunden werden. Damit kann die OBJID zugeordnet werden.
       Fallback 1: Wenn keine Zuordnung zu einem Mietobjekt gelingt, weil keine OBID im Verwendungszweck enthalten ist,
       der Mieter aber genau eine Wohneinheit zugeordnet hat, dann ist diese Zuornung anzunehmen.
       Fallback 2: Würde im selben Monat bei einem konkreten Mieter die Objektzuordnung 2 mal erfolgen, dann ist der grössere Betrag dem Objekttyp Wohnung
       und der kleinere Betrag dem Objekttyp Garage zuzuordnen.
       Warnung, wenn die Objektzuordnung nicht gelingt oder wenn der selbe Mieter in einem Monat keinmal oder
       mehr als einmal Betriebskosten für die idente Wohneinheit eine Überweisung gemacht hat.
       Warnung, wenn in einem Monat ein Objekt keine Betriebskostenzuordnung bekommen hat.
     > Buchungstyp Rücküberweisung: Partner muss eine Hausverwaltung sein und der Betrag muss positiv sein (Eingang).
       Es handelt sich um eine Rückzahlung/Gutschrift von der Hausverwaltung an den Vermieter.
       Die OBID wird über die HVID im Text zugeordnet (gleiche Logik wie bei Betriebskosten).
       Warnung, wenn die Objektzuordnung nicht gelingt.
3) ZUSÄTZLICHE REGELN zur Buchungstyp-Erkennung:
   - Wenn der Partner einer Buchung eine Hausverwaltung ist, dann geht es im Zweifel um Betriebskosten (bei negativem Betrag) oder Rücküberweisung (bei positivem Betrag).
   - Bei Mietern: Wenn man die TopNummer (Teil der OBID, z.B. "T34" aus "H26T34") im Umsatztext findet,
     dann geht es im Zweifel um Miete.
   - Bei Mietern: Wenn man die HVID oder einen Teil davon im Umsatztext findet, dann geht es um Betriebskosten.
4) FUZZY-SUCHE als Fallback für Objektzuordnung:
   - Wenn die exakte OBID nicht im Text gefunden wird, aber Teile davon schon, dann Fuzzy-Match versuchen.
   - Beispiel: "h2640" im Text matcht "H26T40", weil sowohl "h26" als auch "40" enthalten sind.
   - Die Fuzzy-Suche zerlegt die OBID in Prefix (z.B. "H26") und Nummer (z.B. "40") und prüft ob beide im Text vorkommen.
   - Auch nur die Zahlen (z.B. "26" und "40") reichen für einen Fuzzy-Match aus.
5) FALLBACK-REGELN für Mieter:
   - Wenn keine Zuordnung möglich war und der Mieter nur eine Wohnung hat, wird diese Wohnung angenommen.
   - Für den Buchungstyp: Wenn TopNummer oder Fuzzy-Match gefunden → Miete; ansonsten → Betriebskosten.
   - Texte wie 'sonst', 'sonstige', 'zahlung' deuten auf Betriebskosten hin.
   - Feld Kommentar: Texte aus dem Verwendungszweck sowie der Felder Kategorie, Notiz, Mandat ID, Auftraggeberreferenz, Eigene Referenz,
     Verdichtung: 'strasse'->'str', 'straße'->'str', 'betriebskosten'->'bk', Leerzeichen entfernen, alles in Kleinbuchstaben.
   - Bei allen Warnungen ist immer die Zeilennummer in umsaetze.csv, das Valutadatum und was wem nicht zugeordnet werden konnte anzugeben.
9) OUTPUT out_summary.csv:
   - Die zweite von diesem Analyse-Script erstellte Datei, die out_analyse.csv zusammenfasst.
   - CSV mit Separator=;, 1. Zeile = Header, UTF-8, nur LF line terminators
   - Felder: Titel;Dimension;Gruppierung1;Gruppierung2;Saldo;SummePositiveBeträge;SummeNegativeBeträge;AnzahlBuchungen
   - Feld Titel: Beschreibender Text für die Art der Gruppierung (z.B. "Monat/Buchungstyp/OBID", "Total/IBAN")
   - Feld Dimension: Kann die Werte "Total" (alle Buchungen) oder "JJJJ-MM" (Monat des Valutadatums) annehmen
   - Feld Gruppierung1: Erste Gruppierungsebene (Buchungstyp, OBID, oder Partner-IBAN mit Partnername)
   - Feld Gruppierung2: Zweite Gruppierungsebene (OBID, Partner-IBAN mit Partnername, Objekttyp, oder "keine")
   - Feld Saldo: Summe aller Beträge (positive + negative) für diese Gruppierung
   - Feld SummePositiveBeträge: Summe nur der positiven Beträge (Eingänge)
   - Feld SummeNegativeBeträge: Summe nur der negativen Beträge (Abgänge)
   - Feld AnzahlBuchungen: Anzahl der Buchungen in dieser Gruppierung
   - WICHTIG: Bei Partner-IBAN wird das Format "IBAN (Partnername)" verwendet für bessere Lesbarkeit
   - Erstelle folgende Ausgaben (Titel, Dimension, Gruppierung1, Gruppierung2):
     > Titel="Monat/Buchungstyp/OBID", Dimension=JJJJ-MM, Gruppierung1=Buchungstyp, Gruppierung2=OBID
     > Titel="Monat/Buchungstyp/IBAN", Dimension=JJJJ-MM, Gruppierung1=Buchungstyp, Gruppierung2="IBAN (Partnername)"
     > Titel="Monat/OBID/Objekttyp", Dimension=JJJJ-MM, Gruppierung1=OBID, Gruppierung2=Objekttyp
     > Titel="Monat/OBID", Dimension=JJJJ-MM, Gruppierung1=OBID, Gruppierung2="keine"
     > Titel="Monat/IBAN/Objekttyp", Dimension=JJJJ-MM, Gruppierung1="IBAN (Partnername)", Gruppierung2=Objekttyp
     > Titel="Total/IBAN", Dimension="Total", Gruppierung1="IBAN (Partnername)", Gruppierung2="keine"
10) OUTPUT out_JJJJMM.txt und out_JJJJMM.md (pro Monat):
   - Tabellarische Übersicht der Wohneinheiten pro Monat, userfriendly formatiert
   - Pro Monat werden zwei Dateien erstellt: eine als Fixed-Width-Text (.txt) und eine als Markdown-Tabelle (.md)
   - JJJJMM ist das Monatskürzel ohne Bindestrich (z.B. 202601 für Jänner 2026)
   - Jede OBID (Wohnung UND Garage) bekommt eine eigene Zeile
   - Spalten: OBID, Mietername, Miete, BKMi, BKHV, Diag, Reparatur, Energie
     > Miete: Mietzahlung für dieses Objekt (Eingang)
     > BKMi: Betriebskosten vom Mieter (Eingang, typischerweise positiv)
     > BKHV: Betriebskosten an die Hausverwaltung NETTO (Ausgang + Rücküberweisung, enthält also auch Rücküberweisungen der HV)
     > Diag: Diagnose W/G (w/g bei Eigennutzung) + <, >, = für BKMi vs |BKHV|
     > Reparatur: Reparaturkosten (Ausgang, negativ)
     > Energie: Energiekosten (Ausgang, negativ, z.B. IKB)
   - Zuordnung BKMi vs BKHV erfolgt über den Partnertyp der Buchung
   - Eigennutzung (Vermieter-IBAN bei Wohneinheit): Diag-Prefix wird kleingeschrieben (w/g statt W/G)
   - Primärer Mieter wird über die tatsächlichen Mietzahlungen ermittelt (nicht über die Reihenfolge in partner.csv)
   - Sortierung: Wohnungen nach OBID, zugehörige Garagen (gleiche IBAN) direkt danach, verwaiste Garagen am Ende
   - SUMME-Zeile mit Spaltensummen, Beträge mit Wert 0.00 als leer
   - Nach der Tabelle folgen (falls vorhanden):
     > Reparaturen: Datum, OBID, Betrieb, Betrag, Beschreibung (aus Kommentar)
     > Kautionen: OBID, Mietername, Betrag von/an Mieter, Vermieter-Betrag
     > Eigenentnahmen: Datum, Betrag, Empfängerkonto
   - Bei IBAN-Kollision (gleiche IBAN für Vermieter und Mieter) wird der Mietername bevorzugt
11) OUTPUT out_mieten.xlsx:
   - Excel-Datei mit mehreren Sheets: Analyse, Summary, Monatsübersicht, Plausibilität
   - Sheet Analyse: Detaillierte Buchungsanalyse mit farbcodierten Beträgen (grün=positiv, rot=negativ)
   - Sheet Summary: Zusammenfassungen gruppiert nach verschiedenen Dimensionen
   - Sheet Monatsübersicht: Pivot-Tabelle Monat x OBID mit Miete und BK pro Objekt
   - Sheet Plausibilität: Auffälligkeiten mit farblicher Markierung (gelb=Warnung, rot=kritisch)
12) PLAUSIBILITÄTSPRÜFUNG:
   - Mietpreis-Schwankungen: Warnung bei >5% Abweichung zum Vormonat pro OBID
   - Doppelzahlungen: Gleicher Mieter, Betrag, Monat und OBID bei Miete/BK
   - Unkategorisierte Buchungen: Buchungen mit Typ "Sonstiges" werden gemeldet
   - Hohe Einzelbeträge: Buchungen >5000 EUR (außer Kaution) werden gemeldet
"""

import pandas as pd
import re
from collections import defaultdict
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter

def validate_iban_checksum(iban_str):
    """
    Validiert die IBAN-Prüfsumme nach ISO 7064 (Modulo 97).
    """
    if not iban_str or pd.isna(iban_str) or iban_str == '':
        return False
    
    # Entferne Leerzeichen
    iban = iban_str.replace(' ', '').upper()
    
    # IBAN muss mindestens 15 Zeichen haben
    if len(iban) < 15:
        return False
    
    # Verschiebe die ersten 4 Zeichen ans Ende
    rearranged = iban[4:] + iban[:4]
    
    # Ersetze Buchstaben durch Zahlen (A=10, B=11, ..., Z=35)
    numeric_iban = ''
    for char in rearranged:
        if char.isdigit():
            numeric_iban += char
        elif char.isalpha():
            numeric_iban += str(ord(char) - ord('A') + 10)
        else:
            return False
    
    # Prüfe Modulo 97
    try:
        return int(numeric_iban) % 97 == 1
    except ValueError:
        return False

def load_partner_csv(filepath):
    """
    Lädt partner.csv und erstellt die erforderlichen Datenstrukturen.
    """
    # Lese die Datei mit UTF-8 Encoding und BOM
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    # Filtere Kommentarzeilen und Leerzeilen
    filtered_lines = []
    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        # Ignoriere Leerzeilen und Zeilen die mit # beginnen
        if stripped == '' or stripped.startswith('#'):
            continue
        filtered_lines.append((line_num, line))
    
    # Parse Header
    header_line_num, header_line = filtered_lines[0]
    header = [col.strip() for col in header_line.strip().split(';')]
    
    # Parse Datenzeilen
    partner_table = {}  # Key: Partner-IBAN
    obid_to_info = {}   # Key: OBID -> {HVID, EVID}
    hvid_to_obid = {}   # Key: HVID -> OBID
    evid_to_obid = {}   # Key: EVID -> OBID
    mieter_table = []   # List of {IBAN, OBID, HVID, EVID, Objekttyp}
    wohneinheiten_table = []  # List of {OBID, IBAN, Objekttyp}
    
    bank_count = 0
    
    for line_num, line in filtered_lines[1:]:
        parts = [p.strip() for p in line.strip().split(';')]
        
        if len(parts) < len(header):
            parts.extend([''] * (len(header) - len(parts)))
        
        row = dict(zip(header, parts))
        
        partnertyp = row.get('Partnertyp', '')
        obid = row.get('OBID', '').strip()
        hvid = row.get('HVID', '').strip()
        evid = row.get('EVID', '').strip()
        objekttyp = row.get('Objekttyp', '').strip()
        partnername = row.get('Partnername', '').strip()
        partner_iban = row.get('Partner-IBAN', '').strip()
        
        # Bank-Spezialfall
        if partnertyp == 'Bank':
            bank_count += 1
            if bank_count > 1:
                print(f"WARNUNG (partner.csv, Zeile {line_num}): Bank darf nur einmal vorkommen.")
            partner_table['NOIBAN'] = {'Name': partnername, 'Typ': 'Bank'}
            continue
        
        # IBAN Validierung
        if not partner_iban:
            print(f"WARNUNG (partner.csv, Zeile {line_num}): Partner-IBAN fehlt für {partnername}.")
        elif not validate_iban_checksum(partner_iban):
            print(f"WARNUNG (partner.csv, Zeile {line_num}): IBAN-Prüfsumme nicht korrekt für {partner_iban}.")
        
        # Partner-Table: Bei Duplikaten wird eine Liste geführt
        if partner_iban:
            if partner_iban not in partner_table:
                partner_table[partner_iban] = {'Name': partnername, 'Typ': partnertyp}
            else:
                # Merke zusätzliche Typen für diese IBAN
                existing = partner_table[partner_iban]
                if 'AlternativeTypen' not in existing:
                    existing['AlternativeTypen'] = []
                existing['AlternativeTypen'].append({'Name': partnername, 'Typ': partnertyp})
        
        # Mieter-spezifische Verarbeitung
        if partnertyp == 'Mieter' and obid and obid.lower() not in ['alle', 'diverse']:
            # OBID-Tabellen
            if obid not in obid_to_info:
                obid_to_info[obid] = {'HVID': hvid if hvid else '', 
                                     'EVID': evid if evid else '', 
                                     'Objekttyp': objekttyp if objekttyp else ''}
            
            if hvid and hvid not in hvid_to_obid:
                hvid_to_obid[hvid] = obid
            
            if evid and evid not in evid_to_obid:
                evid_to_obid[evid] = obid
            
            # Mieter-Table
            mieter_table.append({
                'IBAN': partner_iban,
                'OBID': obid,
                'HVID': hvid if hvid else '',
                'EVID': evid if evid else '',
                'Objekttyp': objekttyp if objekttyp else ''
            })
            
            # Wohneinheiten-Table
            wohneinheiten_table.append({
                'OBID': obid,
                'IBAN': partner_iban,
                'Objekttyp': objekttyp if objekttyp else ''
            })
    
    return {
        'partner_table': partner_table,
        'obid_to_info': obid_to_info,
        'hvid_to_obid': hvid_to_obid,
        'evid_to_obid': evid_to_obid,
        'mieter_table': mieter_table,
        'wohneinheiten_table': wohneinheiten_table
    }

def verdichte_kommentar(row):
    """
    Erstellt verdichteten Kommentar aus verschiedenen Feldern.
    """
    fields = ['Verwendungszweck', 'Kategorie', 'Notiz', 'Mandat ID', 
              'Auftraggeberreferenz', 'Eigene Referenz']
    
    parts = []
    for field in fields:
        val = row.get(field, '')
        if val and not pd.isna(val):
            parts.append(str(val))
    
    kommentar = ' '.join(parts)
    
    # Verdichtung
    kommentar = kommentar.lower()
    kommentar = kommentar.replace('strasse', 'str')
    kommentar = kommentar.replace('straße', 'str')
    kommentar = kommentar.replace('betriebskosten', 'bk')
    kommentar = kommentar.replace(' ', '')
    
    return kommentar

def extract_obid_number(obid):
    """
    Extrahiert die Zahl am Ende der OBID nach dem letzten Buchstaben.
    """
    if not obid:
        return ''
    # Finde alle Zahlen am Ende
    match = re.search(r'(\d+)$', obid)
    if match:
        return match.group(1)
    return ''

def find_object_assignment(row, partner_info, tables, buchungstyp_hint=None, csv_line=None, valutadatum=None):
    """
    Findet die Objektzuordnung basierend auf dem Buchungstext.
    """
    partnertyp = partner_info['Typ']
    partner_iban = row.get('Partner-IBAN', '')

    # Kombinierter Suchtext
    search_fields = ['Buchungstext', 'Umsatztext', 'Verwendungszweck',
                     'Name des Partners', 'Zahlungsreferenz', 'Auftraggeberreferenz']
    search_text = ' '.join([str(row.get(f, '')) for f in search_fields]).lower()

    # Bei Vermieter-Kaution: ZUERST nach Mieternamen suchen (hat Vorrang vor OBID im Text)
    if buchungstyp_hint == 'Kaution' and partnertyp == 'Vermieter':
        found_mieter_units = []
        for iban, pinfo in tables['partner_table'].items():
            if pinfo.get('Typ') == 'Mieter':
                mieter_name = pinfo.get('Name', '').lower()
                # Extrahiere Nachname (letztes Wort oder erstes Wort wenn nur ein Wort)
                name_parts = mieter_name.split()
                if name_parts:
                    nachname = name_parts[-1] if len(name_parts) > 1 else name_parts[0]
                    # Suche Nachname im Text (mindestens 4 Zeichen)
                    if len(nachname) >= 4 and nachname in search_text:
                        # Finde die Wohneinheiten dieses Mieters
                        units = [m for m in tables['mieter_table'] if m['IBAN'] == iban]
                        found_mieter_units.extend(units)

        if found_mieter_units:
            # Bevorzuge Wohnungen
            wohnungen = [u for u in found_mieter_units if u.get('Objekttyp') == 'Wohnung']
            if wohnungen:
                unit = wohnungen[0]
                # Prüfe ob eine andere OBID im Text steht (Warnung)
                search_norm = search_text.replace(' ', '').replace('-', '')
                for obid in tables['obid_to_info'].keys():
                    obid_norm = obid.lower().replace(' ', '').replace('-', '')
                    if obid_norm in search_norm and obid != unit['OBID']:
                        if csv_line and valutadatum:
                            print(f"WARNUNG (umsaetze.csv, Zeile {csv_line}, {valutadatum}): "
                                  f"OBID {obid} im Text gefunden, aber Mieter gehört zu {unit['OBID']}. Verwende {unit['OBID']}.")
                        break
                return {
                    'OBID': unit['OBID'],
                    'HVID': unit['HVID'],
                    'EVID': unit['EVID'],
                    'Objekttyp': unit['Objekttyp']
                }
            elif found_mieter_units:
                unit = found_mieter_units[0]
                return {
                    'OBID': unit['OBID'],
                    'HVID': unit['HVID'],
                    'EVID': unit['EVID'],
                    'Objekttyp': unit['Objekttyp']
                }

    # Für Energieversorger: Suche EVID
    if partnertyp == 'Energieversorger':
        for evid, obid in tables['evid_to_obid'].items():
            if evid and str(evid) in search_text:
                info = tables['obid_to_info'].get(obid, {})
                return {
                    'OBID': obid,
                    'HVID': info.get('HVID', ''),
                    'EVID': evid,
                    'Objekttyp': info.get('Objekttyp', '')
                }
        return None
    
    # Für Hausverwaltung: Suche HVID
    if partnertyp == 'Hausverwaltung':
        # Normalisiere Suchtext
        search_norm = search_text.replace(' ', '').replace('-', '')

        # STRATEGIE 1: Suche zuerst nach OBID im Text (höchste Priorität)
        for obid, info in tables['obid_to_info'].items():
            obid_norm = obid.lower().replace(' ', '').replace('-', '')
            if obid_norm in search_norm:
                hvid = info.get('HVID', '')
                return {
                    'OBID': obid,
                    'HVID': hvid,
                    'EVID': info.get('EVID', ''),
                    'Objekttyp': info.get('Objekttyp', '')
                }

        # STRATEGIE 2: Suche nach HVID, sortiert nach Länge (längste zuerst)
        hvid_items = [(hvid, obid) for hvid, obid in tables['hvid_to_obid'].items() if hvid]
        hvid_items.sort(key=lambda x: len(str(x[0])), reverse=True)

        for hvid, obid in hvid_items:
            hvid_str = str(hvid).strip()
            # Suche mit Wortgrenzen: /HVID, HVID/, -HVID, HVID-, oder Leerzeichen
            patterns = [
                f'/{hvid_str}',
                f'{hvid_str}/',
                f'-{hvid_str}',
                f'{hvid_str}-',
                f' {hvid_str} ',
                f' {hvid_str}/',
                f'/{hvid_str} '
            ]
            for pattern in patterns:
                if pattern in search_text:
                    info = tables['obid_to_info'].get(obid, {})
                    return {
                        'OBID': obid,
                        'HVID': hvid,
                        'EVID': info.get('EVID', ''),
                        'Objekttyp': info.get('Objekttyp', '')
                    }

        return None
    
    # Für Mieter, Vermieter, Handwerker: Suche OBID/HVID/Nummer
    possible_obids = []
    
    if partnertyp == 'Mieter':
        # Nur OBIDs die diesem Mieter zugeordnet sind
        possible_obids = [m['OBID'] for m in tables['mieter_table'] 
                         if m['IBAN'] == partner_iban]
    else:
        # Alle OBIDs
        possible_obids = list(tables['obid_to_info'].keys())
    
    # Sammle alle Matches mit ihrer Priorität und Match-Länge
    matches = []
    
    for obid in possible_obids:
        info = tables['obid_to_info'].get(obid, {})
        hvid = info.get('HVID', '')
        
        # Normalisiere Suchtexte (ohne Leerzeichen)
        search_norm = search_text.replace(' ', '').replace('-', '')
        
        # Methode 1: Vollständige OBID (höchste Priorität)
        obid_norm = obid.lower().replace(' ', '').replace('-', '')
        if obid_norm in search_norm:
            matches.append((1, len(obid_norm), obid, hvid, info))
            continue
        
        # Methode 2: HVID (zweithöchste Priorität)
        if hvid:
            hvid_norm = hvid.lower().replace(' ', '').replace('-', '')
            if hvid_norm in search_norm:
                matches.append((2, len(hvid_norm), obid, hvid, info))
                continue
        
        # Methode 3: Suffix der OBID (z.B. "F15", "TG101", "T34", "A19")
        match = re.search(r'([A-Z]+\d+)$', obid, re.IGNORECASE)
        if match:
            suffix = match.group(1).lower()
            if suffix in search_norm:
                matches.append((3, len(suffix), obid, hvid, info))
                continue
        
        # Methode 4: Nur Nummer am Ende (niedrigste Priorität, mindestens 2 Ziffern)
        obid_num = extract_obid_number(obid)
        if obid_num and len(obid_num) >= 2 and obid_num in search_norm:
            matches.append((4, len(obid_num), obid, hvid, info))
            continue

        # Methode 5: Fuzzy-Suche - Prefix UND Nummer müssen beide im Text vorkommen
        # z.B. "h2640" matcht "H26T40" weil "h26" und "40" enthalten sind
        fuzzy_match = re.match(r'^([A-Z]+)(\d+)([A-Z]*)(\d+)$', obid, re.IGNORECASE)
        if fuzzy_match:
            prefix_letters = fuzzy_match.group(1).lower()  # z.B. "h"
            prefix_num = fuzzy_match.group(2)              # z.B. "26"
            nummer = fuzzy_match.group(4)                  # z.B. "40"
            full_prefix = (prefix_letters + prefix_num).lower()  # z.B. "h26"

            # Variante 1: Volles Prefix + Nummer (z.B. "h26" + "40")
            if full_prefix in search_norm and nummer in search_norm:
                matches.append((5, len(full_prefix) + len(nummer), obid, hvid, info))
            # Variante 2: Nur die Zahlen (z.B. "26" + "40")
            elif prefix_num in search_norm and nummer in search_norm:
                matches.append((6, len(prefix_num) + len(nummer), obid, hvid, info))

    # Wähle das beste Match: niedrigste Priorität, dann längste Match-Länge
    if matches:
        # Sortiere nach Priorität (aufsteigend) und Match-Länge (absteigend)
        matches.sort(key=lambda x: (x[0], -x[1]))
        best_match = matches[0]
        obid, hvid, info = best_match[2], best_match[3], best_match[4]
        return {
            'OBID': obid,
            'HVID': hvid,
            'EVID': info.get('EVID', ''),
            'Objekttyp': info.get('Objekttyp', '')
        }
    
    # Fallback 1: Wenn Mieter nur eine Wohneinheit hat
    if partnertyp == 'Mieter':
        mieter_units = [m for m in tables['mieter_table'] 
                       if m['IBAN'] == partner_iban]
        if len(mieter_units) == 1:
            unit = mieter_units[0]
            return {
                'OBID': unit['OBID'],
                'HVID': unit['HVID'],
                'EVID': unit['EVID'],
                'Objekttyp': unit['Objekttyp']
            }
    
    # Für Kaution: Wenn keine direkte Zuordnung, aber eindeutig zuordenbar
    if buchungstyp_hint == 'Kaution' and partnertyp in ['Mieter', 'Vermieter']:
        if partnertyp == 'Mieter':
            mieter_units = [m for m in tables['mieter_table']
                           if m['IBAN'] == partner_iban]
        else:
            # Bei Vermieter-Kaution: Suche nach Mieternamen im Text
            found_mieter_units = []
            for iban, pinfo in tables['partner_table'].items():
                if pinfo.get('Typ') == 'Mieter':
                    mieter_name = pinfo.get('Name', '').lower()
                    # Extrahiere Nachname (letztes Wort oder erstes Wort wenn nur ein Wort)
                    name_parts = mieter_name.split()
                    if name_parts:
                        nachname = name_parts[-1] if len(name_parts) > 1 else name_parts[0]
                        # Suche Nachname im Text (mindestens 4 Zeichen)
                        if len(nachname) >= 4 and nachname in search_text:
                            # Finde die Wohneinheiten dieses Mieters
                            units = [m for m in tables['mieter_table'] if m['IBAN'] == iban]
                            found_mieter_units.extend(units)

            if found_mieter_units:
                # Bevorzuge Wohnungen
                wohnungen = [u for u in found_mieter_units if u.get('Objekttyp') == 'Wohnung']
                if len(wohnungen) >= 1:
                    unit = wohnungen[0]
                    return {
                        'OBID': unit['OBID'],
                        'HVID': unit['HVID'],
                        'EVID': unit['EVID'],
                        'Objekttyp': unit['Objekttyp']
                    }
                elif len(found_mieter_units) >= 1:
                    unit = found_mieter_units[0]
                    return {
                        'OBID': unit['OBID'],
                        'HVID': unit['HVID'],
                        'EVID': unit['EVID'],
                        'Objekttyp': unit['Objekttyp']
                    }

            # Fallback: Alle Wohneinheiten
            mieter_units = list(tables['obid_to_info'].items())
            mieter_units = [{'OBID': k, 'HVID': v.get('HVID', ''),
                           'EVID': v.get('EVID', ''),
                           'Objekttyp': v.get('Objekttyp', '')}
                          for k, v in mieter_units]

        # Bevorzuge Wohnung wenn Wohnung und Garage vorhanden
        wohnungen = [u for u in mieter_units if u['Objekttyp'] == 'Wohnung']
        if len(wohnungen) == 1:
            unit = wohnungen[0]
            return {
                'OBID': unit['OBID'],
                'HVID': unit['HVID'],
                'EVID': unit['EVID'],
                'Objekttyp': unit['Objekttyp']
            }
        elif len(mieter_units) == 1:
            unit = mieter_units[0]
            return {
                'OBID': unit['OBID'],
                'HVID': unit['HVID'],
                'EVID': unit['EVID'],
                'Objekttyp': unit['Objekttyp']
            }
    
    return None

def process_umsaetze(filepath, tables):
    """
    Verarbeitet umsaetze.csv und erstellt out_analyse.csv.
    """
    # Lese CSV mit ISO-8859-1 Encoding, Partner-IBAN als String
    df = pd.read_csv(filepath, sep=';', encoding='iso-8859-1',
                     dtype={'Kontoverbindung des Partners': str, 'IBAN': str})
    
    output_rows = []
    
    for idx, row in df.iterrows():
        csv_line = idx + 2  # +2 wegen Header und 0-basiertem Index
        
        # Ignoriere Verständigung
        buchungstext = str(row.get('Buchungstext', '')).lower()
        if 'verständigung' in buchungstext:
            continue
        
        # Währungsprüfung
        waehrung = row.get('Waehrung', '')
        if waehrung != 'EUR':
            valuta = row.get('Valutadatum', '')
            print(f"WARNUNG (umsaetze.csv, Zeile {csv_line}, {valuta}): "
                  f"Währung ist {waehrung}, nicht EUR. Zeile wird ignoriert.")
            continue
        
        # Basis-Informationen
        valutadatum = row.get('Valutadatum', '')
        betrag_raw = row.get('Betrag', 0)
        # Konvertiere Betrag zu float (deutsches Format: Punkt=Tausendertrenner, Komma=Dezimaltrenner)
        try:
            if isinstance(betrag_raw, str):
                # Zuerst Tausendertrenner (Punkt) entfernen, dann Komma durch Punkt ersetzen
                betrag_str = betrag_raw.replace('.', '').replace(',', '.')
                betrag = round(float(betrag_str), 2)
            else:
                betrag = round(float(betrag_raw), 2)
        except (ValueError, TypeError):
            betrag = 0.0
        partner_iban = str(row.get('Kontoverbindung des Partners', '')).strip()
        
        # Monat für Gruppierung
        monat = valutadatum[:7] if len(valutadatum) >= 7 else ''
        
        # Initialisiere Ergebnis-Zeile
        result = {
            'Valutadatum': valutadatum,
            'Buchungstyp': 'Sonstiges',
            'Objekttyp': '',
            'OBID': '',
            'HVID': '',
            'EVID': '',
            'Partner-IBAN': partner_iban,
            'Partnername': '',
            'Betrag': betrag,
            'Kommentar': verdichte_kommentar(row),
            'Monat': monat
        }
        
        # Kombinierter Suchtext
        search_fields = ['Buchungstext', 'Umsatztext', 'Verwendungszweck',
                        'Name des Partners', 'Zahlungsreferenz', 'Auftraggeberreferenz']
        combined_text = ' '.join([str(row.get(f, '')) for f in search_fields]).lower()
        
        # Spezialfall Abschluss
        if 'abschluss' in buchungstext:
            result.update({
                'Buchungstyp': 'Abschluss',
                'Partner-IBAN': 'NOIBAN',
                'Partnername': 'BANK'
            })
            output_rows.append(result)
            continue
        
        # Partner-IBAN Warnung
        if not partner_iban:
            print(f"WARNUNG (umsaetze.csv, Zeile {csv_line}, {valutadatum}): "
                  f"Keine Partner-IBAN vorhanden.")
            output_rows.append(result)
            continue
        
        # Partner identifizieren
        partner_info = tables['partner_table'].get(partner_iban)
        if not partner_info:
            print(f"WARNUNG (umsaetze.csv, Zeile {csv_line}, {valutadatum}): "
                  f"Partner-IBAN {partner_iban} ist unbekannt.")
            output_rows.append(result)
            continue

        # Bei IBAN-Duplikaten: Kontextabhängig den richtigen Partner wählen
        # Wenn die IBAN sowohl Vermieter als auch Mieter ist (Eigennutzung),
        # und der Betrag positiv ist (Eingang), prüfe ob ein Mieter-Eintrag existiert
        if 'AlternativeTypen' in partner_info and betrag > 0:
            alt_mieter = [a for a in partner_info['AlternativeTypen'] if a['Typ'] == 'Mieter']
            if alt_mieter:
                partner_info = alt_mieter[0]

        result['Partnername'] = partner_info['Name']
        partnertyp = partner_info['Typ']
        
        # Buchungstyp bestimmen
        buchungstyp = 'Sonstiges'
        
        if partnertyp == 'Energieversorger':
            buchungstyp = 'Energiekosten'
        elif partnertyp == 'Finanzamt':
            buchungstyp = 'Steuer'
        elif partnertyp in ['Beratung', 'Berater']:
            buchungstyp = 'Beratung'
        elif partnertyp == 'Spende':
            buchungstyp = 'Spende'
        elif partnertyp == 'Versorgung':
            buchungstyp = 'Versorgung'
        elif partnertyp == 'Handwerker':
            buchungstyp = 'Reparatur'
        elif partnertyp == 'Vermieter':
            if 'kaution' in combined_text:
                buchungstyp = 'Kaution'
            else:
                buchungstyp = 'Eigenentnahme'
        elif partnertyp in ['Mieter', 'Hausverwaltung']:
            # Prüfe zuerst auf Kaution
            if 'kaution' in combined_text:
                buchungstyp = 'Kaution'
            # Dann auf Miete (hat Vorrang vor Betriebskosten)
            elif 'miete' in combined_text:
                buchungstyp = 'Miete'
            # Dann auf Betriebskosten (explizite Keywords)
            elif any(x in combined_text for x in ['betriebskosten', ' bk ', 'vorschreibung', 'vorschr.', 'nebenkosten', 'sonst.zahlung', 'sonstigekosten']):
                buchungstyp = 'Betriebskosten'
            # Kostenersatz nur für Mieter
            elif partnertyp == 'Mieter' and 'kostenersatz' in combined_text:
                buchungstyp = 'Kostenersatz'
            # Zusätzliche Regeln im Zweifel:
            elif partnertyp == 'Hausverwaltung':
                # Hausverwaltung: positiv = Rücküberweisung, negativ = Betriebskosten
                if betrag > 0:
                    buchungstyp = 'Rücküberweisung'
                else:
                    buchungstyp = 'Betriebskosten'
            elif partnertyp == 'Mieter':
                # Bei Mietern: Prüfe ob TopNummer, HVID oder Fuzzy-Match im Text vorkommt
                mieter_units = [m for m in tables['mieter_table'] if m['IBAN'] == partner_iban]
                found_hvid = False
                found_topnr = False
                found_fuzzy = False
                search_norm = combined_text.replace(' ', '').replace('-', '')

                for unit in mieter_units:
                    # Prüfe HVID
                    hvid = unit.get('HVID', '')
                    if hvid:
                        hvid_norm = str(hvid).lower().replace(' ', '').replace('-', '')
                        if hvid_norm and hvid_norm in search_norm:
                            found_hvid = True
                            break

                    # Prüfe TopNummer (z.B. "T34" aus "H26T34", "TG101" aus "T132TG101")
                    obid = unit.get('OBID', '')
                    if obid:
                        match = re.search(r'([A-Z]+\d+)$', obid, re.IGNORECASE)
                        if match:
                            topnr = match.group(1).lower()
                            if topnr in search_norm:
                                found_topnr = True

                        # Fuzzy-Suche: Prefix UND Nummer (z.B. "h26" und "40" oder nur "26" und "40" für "H26T40")
                        fuzzy_match = re.match(r'^([A-Z]+)(\d+)([A-Z]*)(\d+)$', obid, re.IGNORECASE)
                        if fuzzy_match:
                            prefix_letters = fuzzy_match.group(1).lower()
                            prefix_num = fuzzy_match.group(2)
                            nummer = fuzzy_match.group(4)
                            full_prefix = prefix_letters + prefix_num
                            # Variante 1: Volles Prefix + Nummer
                            if full_prefix in search_norm and nummer in search_norm:
                                found_fuzzy = True
                            # Variante 2: Nur die Zahlen
                            elif prefix_num in search_norm and nummer in search_norm:
                                found_fuzzy = True

                # HVID gefunden → Betriebskosten, TopNummer oder Fuzzy gefunden → Miete
                if found_hvid:
                    buchungstyp = 'Betriebskosten'
                elif found_topnr or found_fuzzy:
                    buchungstyp = 'Miete'
                else:
                    # Letzter Fallback: Mieter mit nur einer Wohnung → Betriebskosten
                    wohnungen = [u for u in mieter_units if u.get('Objekttyp') == 'Wohnung']
                    if len(wohnungen) == 1:
                        buchungstyp = 'Betriebskosten'
        
        result['Buchungstyp'] = buchungstyp
        
        # Objektzuordnung versuchen
        obj_assignment = None
        
        if buchungstyp in ['Energiekosten', 'Reparatur', 'Kostenersatz', 'Kaution',
                          'Miete', 'Betriebskosten', 'Rücküberweisung']:
            # Setze Partner-IBAN in row für find_object_assignment
            row_copy = row.copy()
            row_copy['Partner-IBAN'] = partner_iban
            obj_assignment = find_object_assignment(row_copy, partner_info, tables, buchungstyp, csv_line, valutadatum)
            
            if obj_assignment:
                result.update(obj_assignment)
            else:
                # Warnung ausgeben
                if partnertyp in ['Mieter', 'Energieversorger', 'Hausverwaltung', 'Handwerker']:
                    print(f"WARNUNG (umsaetze.csv, Zeile {csv_line}, {valutadatum}): "
                          f"Keine Objektzuordnung für {result['Partnername']} "
                          f"({partnertyp}, Buchungstyp: {buchungstyp}).")
        
        output_rows.append(result)
    
    # Fallback 2: Größe-basierte Zuordnung für Miete/Betriebskosten
    df_output = pd.DataFrame(output_rows)
    
    for (monat, partner_iban_key, buchungstyp), group in df_output.groupby(['Monat', 'Partner-IBAN', 'Buchungstyp']):
        if buchungstyp in ['Miete', 'Betriebskosten'] and len(group) >= 2:
            # Finde Mieter-Einträge für diesen Partner
            partner_units = [m for m in tables['mieter_table'] 
                           if m['IBAN'] == partner_iban_key]
            
            # Sortiere nach Betrag (absolut, absteigend)
            sorted_group = group.sort_values('Betrag', key=abs, ascending=False)
            
            # Größter Betrag = Wohnung
            if len(sorted_group) >= 1:
                idx_wohnung = sorted_group.index[0]
                # Finde Wohnungs-OBID
                wohnung_units = [u for u in partner_units if u['Objekttyp'] == 'Wohnung']
                if wohnung_units:
                    unit = wohnung_units[0]
                    df_output.loc[idx_wohnung, 'Objekttyp'] = 'Wohnung'
                    df_output.loc[idx_wohnung, 'OBID'] = unit['OBID']
                    df_output.loc[idx_wohnung, 'HVID'] = unit['HVID']
                    df_output.loc[idx_wohnung, 'EVID'] = unit['EVID']
            
            # Rest = Garage
            if len(sorted_group) >= 2:
                garage_units = [u for u in partner_units if u['Objekttyp'] == 'Garage']
                for i, idx_garage in enumerate(sorted_group.index[1:]):
                    if i < len(garage_units):
                        unit = garage_units[i]
                        df_output.loc[idx_garage, 'Objekttyp'] = 'Garage'
                        df_output.loc[idx_garage, 'OBID'] = unit['OBID']
                        df_output.loc[idx_garage, 'HVID'] = unit['HVID']
                        df_output.loc[idx_garage, 'EVID'] = unit['EVID']
    
    # Monats-Vollständigkeitsprüfung: Warnung wenn Objekt ohne Miete oder BK
    alle_wohnungen = [obid for obid, info in tables['obid_to_info'].items()
                      if info.get('Objekttyp') == 'Wohnung']
    for monat in df_output['Monat'].unique():
        if not monat:
            continue
        monat_df = df_output[df_output['Monat'] == monat]
        for obid in alle_wohnungen:
            obj_monat = monat_df[monat_df['OBID'] == obid]
            if not any(obj_monat['Buchungstyp'] == 'Miete'):
                print(f"WARNUNG (Vollständigkeit, {monat}): Objekt {obid} hat keine Mietzuordnung.")
            if not any(obj_monat['Buchungstyp'] == 'Betriebskosten'):
                print(f"WARNUNG (Vollständigkeit, {monat}): Objekt {obid} hat keine BK-Zuordnung.")

    return df_output

def create_summary(df_analyse):
    """
    Erstellt out_summary.csv aus den analysierten Daten.
    """
    summary_rows = []

    # Erstelle IBAN→Partnername Lookup
    iban_to_name = df_analyse.groupby('Partner-IBAN')['Partnername'].first().to_dict()

    def add_summary_row(titel, dim, g1, g2, sub_df):
        """Hilfsfunktion zum Hinzufügen einer Summary-Zeile."""
        positive_sum = sub_df[sub_df['Betrag'] > 0]['Betrag'].sum()
        negative_sum = sub_df[sub_df['Betrag'] < 0]['Betrag'].sum()
        saldo = sub_df['Betrag'].sum()
        anzahl = len(sub_df)

        summary_rows.append({
            'Titel': titel,
            'Dimension': dim,
            'Gruppierung1': g1,
            'Gruppierung2': g2,
            'Saldo': round(saldo, 2),
            'SummePositiveBeträge': round(positive_sum, 2),
            'SummeNegativeBeträge': round(negative_sum, 2),
            'AnzahlBuchungen': anzahl
        })
    
    # Dimension=Monat
    for monat in df_analyse['Monat'].unique():
        if not monat:
            continue
        monat_df = df_analyse[df_analyse['Monat'] == monat]
        
        # Gruppierung1=Buchungstyp, Gruppierung2=OBID
        for (buchungstyp, obid), sub_df in monat_df.groupby(['Buchungstyp', 'OBID']):
            add_summary_row('Monat/Buchungstyp/OBID', monat, buchungstyp, obid if obid else '', sub_df)
        
        # Gruppierung1=Buchungstyp, Gruppierung2=Partner-IBAN
        for (buchungstyp, iban), sub_df in monat_df.groupby(['Buchungstyp', 'Partner-IBAN']):
            iban_display = f"{iban} ({iban_to_name.get(iban, 'Unbekannt')})" if iban else ''
            add_summary_row('Monat/Buchungstyp/IBAN', monat, buchungstyp, iban_display, sub_df)
        
        # Gruppierung1=OBID, Gruppierung2=Objekttyp
        for (obid, objekttyp), sub_df in monat_df.groupby(['OBID', 'Objekttyp']):
            if obid:
                add_summary_row('Monat/OBID/Objekttyp', monat, obid, objekttyp if objekttyp else '', sub_df)
        
        # Gruppierung1=OBID, Gruppierung2=keine
        for obid, sub_df in monat_df.groupby('OBID'):
            if obid:
                add_summary_row('Monat/OBID', monat, obid, 'keine', sub_df)
        
        # Gruppierung1=Partner-IBAN, Gruppierung2=Objekttyp
        for (iban, objekttyp), sub_df in monat_df.groupby(['Partner-IBAN', 'Objekttyp']):
            iban_display = f"{iban} ({iban_to_name.get(iban, 'Unbekannt')})" if iban else ''
            add_summary_row('Monat/IBAN/Objekttyp', monat, iban_display, objekttyp if objekttyp else '', sub_df)
    
    # Dimension=Total
    # Gruppierung1=Partner-IBAN, Gruppierung2=keine
    for iban, sub_df in df_analyse.groupby('Partner-IBAN'):
        iban_display = f"{iban} ({iban_to_name.get(iban, 'Unbekannt')})" if iban else ''
        add_summary_row('Total/IBAN', 'Total', iban_display, 'keine', sub_df)
    
    return pd.DataFrame(summary_rows)

def plausibility_checks(df_analyse, tables):
    """
    Führt Plausibilitätsprüfungen auf den analysierten Daten durch.
    Gibt eine Liste von Findings als Dicts zurück.
    """
    findings = []

    # 1. Mietpreis-Schwankungen: Vergleiche Miete pro OBID zwischen Monaten
    miete_df = df_analyse[df_analyse['Buchungstyp'] == 'Miete'].copy()
    if not miete_df.empty:
        for obid in miete_df['OBID'].unique():
            if not obid:
                continue
            obj_miete = miete_df[miete_df['OBID'] == obid].sort_values('Valutadatum')
            betraege = obj_miete['Betrag'].tolist()
            monate = obj_miete['Monat'].tolist()
            for i in range(1, len(betraege)):
                if betraege[i-1] != 0:
                    abweichung = abs(betraege[i] - betraege[i-1]) / abs(betraege[i-1]) * 100
                    if abweichung > 5:
                        findings.append({
                            'Typ': 'Mietpreis-Änderung',
                            'OBID': obid,
                            'Detail': f"{monate[i-1]}: {betraege[i-1]:.2f} → {monate[i]}: {betraege[i]:.2f} ({abweichung:+.1f}%)"
                        })

    # 2. Doppelzahlungen: Gleicher Mieter, gleicher Betrag, gleicher Monat, gleiche OBID
    for (monat, iban, obid, btyp), group in df_analyse.groupby(['Monat', 'Partner-IBAN', 'OBID', 'Buchungstyp']):
        if btyp in ['Miete', 'Betriebskosten'] and len(group) > 1:
            gleiche = group[group['Betrag'] == group['Betrag'].iloc[0]]
            if len(gleiche) > 1:
                findings.append({
                    'Typ': 'Mögliche Doppelzahlung',
                    'OBID': obid,
                    'Detail': f"{monat}: {btyp} von {group['Partnername'].iloc[0]} - {len(gleiche)}x {gleiche['Betrag'].iloc[0]:.2f} EUR"
                })

    # 3. Sonstiges-Buchungen: Potentiell fehlkategorisiert
    sonstige = df_analyse[df_analyse['Buchungstyp'] == 'Sonstiges']
    if len(sonstige) > 0:
        for _, row in sonstige.iterrows():
            findings.append({
                'Typ': 'Unkategorisiert',
                'OBID': '',
                'Detail': f"{row['Valutadatum']}: {row['Partnername']} ({row['Partner-IBAN']}) - {row['Betrag']:.2f} EUR"
            })

    # 4. Ungewöhnlich hohe Einzelbuchungen (>5000 EUR, außer Kaution)
    grosse = df_analyse[(abs(df_analyse['Betrag']) > 5000) & (df_analyse['Buchungstyp'] != 'Kaution')]
    for _, row in grosse.iterrows():
        findings.append({
            'Typ': 'Hoher Betrag',
            'OBID': row.get('OBID', ''),
            'Detail': f"{row['Valutadatum']}: {row['Buchungstyp']} - {row['Partnername']} - {row['Betrag']:.2f} EUR"
        })

    return findings


def create_monthly_reports(df_analyse, tables):
    """
    Erstellt pro Monat eine tabellarische Übersicht der Wohneinheiten als .txt und .md.
    OBID-basiert: Jede Wohnung und jede Garage bekommt eine eigene Zeile.
    Primärer Mieter = wer tatsächlich Miete zahlt (aus den Buchungsdaten).
    Spalten: OBID, Mietername, Miete, BKMi, BKHV, Reparatur, Energie, Diag
    BKHV enthält Betriebskosten + Rücküberweisungen (netto).
    Diagnose: W/G + <, >, = (z.B. "W =" oder "G <").
    """
    from collections import defaultdict

    # === SCHRITT 1: OBID-basierte Strukturen aufbauen ===
    alle_wohnungen = {obid: info for obid, info in tables['obid_to_info'].items()
                      if info.get('Objekttyp') == 'Wohnung'}
    alle_garagen = {obid: info for obid, info in tables['obid_to_info'].items()
                    if info.get('Objekttyp') == 'Garage'}

    # OBID → Liste möglicher IBANs (aus mieter_table)
    obid_to_ibans = defaultdict(list)
    for entry in tables['mieter_table']:
        obid_to_ibans[entry['OBID']].append(entry['IBAN'])

    # IBAN → Partnername (bevorzugt Mieter-Name bei Kollision)
    def get_mieter_name(iban):
        pi = tables['partner_table'].get(iban, {})
        name = pi.get('Name', '')
        if pi.get('Typ') != 'Mieter' and 'AlternativeTypen' in pi:
            for alt in pi['AlternativeTypen']:
                if alt['Typ'] == 'Mieter':
                    return alt['Name']
        return name

    # Partnertyp-Lookup
    def get_partnertyp(iban):
        pi = tables['partner_table'].get(iban, {})
        typ = pi.get('Typ', '')
        if 'AlternativeTypen' in pi:
            for alt in pi['AlternativeTypen']:
                if alt['Typ'] in ['Mieter', 'Hausverwaltung']:
                    return alt['Typ']
        return typ

    # BK-Split nach Partnertyp + Rücküberweisung
    def get_bk_ruwe(obj_df):
        """Liefert (bk_mieter, bk_hv, rueckueberweisung) für einen OBID."""
        bk_df = obj_df[obj_df['Buchungstyp'] == 'Betriebskosten']
        bk_mieter, bk_hv = 0.0, 0.0
        for _, bk_row in bk_df.iterrows():
            if get_partnertyp(bk_row['Partner-IBAN']) == 'Hausverwaltung':
                bk_hv += bk_row['Betrag']
            else:
                bk_mieter += bk_row['Betrag']
        ruwe = obj_df[obj_df['Buchungstyp'] == 'Rücküberweisung']['Betrag'].sum()
        return bk_mieter, bk_hv, ruwe

    # === SCHRITT 2: Primären Mieter pro OBID bestimmen ===
    miete_df = df_analyse[df_analyse['Buchungstyp'] == 'Miete']
    def primary_mieter_for_obid(obid):
        """Findet den aktuellen Mieter einer OBID anhand der Mietzahlungen."""
        ibans = obid_to_ibans.get(obid, [])
        if not ibans:
            return '', ''
        obj_miete = miete_df[miete_df['OBID'] == obid]
        if not obj_miete.empty:
            latest = obj_miete.sort_values('Valutadatum', ascending=False).iloc[0]
            return latest['Partner-IBAN'], latest['Partnername']
        return ibans[0], get_mieter_name(ibans[0])

    # === SCHRITT 3: Geordnete Liste aller OBIDs (Wohnung + zugehörige Garagen danach) ===
    zugeordnete_garagen = set()
    geordnete_obids = []

    for w_obid in sorted(alle_wohnungen.keys()):
        prim_iban, prim_name = primary_mieter_for_obid(w_obid)
        geordnete_obids.append({
            'OBID': w_obid,
            'Mietername': prim_name,
            'IBAN': prim_iban,
            'Objekttyp': 'Wohnung'
        })
        # Zugehörige Garagen (gleiche IBAN) direkt nach der Wohnung
        for g_obid in sorted(alle_garagen.keys()):
            if g_obid in zugeordnete_garagen:
                continue
            g_ibans = obid_to_ibans.get(g_obid, [])
            if prim_iban and prim_iban in g_ibans:
                g_prim_iban, g_prim_name = primary_mieter_for_obid(g_obid)
                geordnete_obids.append({
                    'OBID': g_obid,
                    'Mietername': g_prim_name if g_prim_name else prim_name,
                    'IBAN': g_prim_iban if g_prim_iban else prim_iban,
                    'Objekttyp': 'Garage'
                })
                zugeordnete_garagen.add(g_obid)

    # Verwaiste Garagen am Ende
    for g_obid in sorted(alle_garagen.keys()):
        if g_obid not in zugeordnete_garagen:
            g_ibans = obid_to_ibans.get(g_obid, [])
            g_iban = g_ibans[0] if g_ibans else ''
            geordnete_obids.append({
                'OBID': g_obid,
                'Mietername': get_mieter_name(g_iban) if g_iban else '',
                'IBAN': g_iban,
                'Objekttyp': 'Garage'
            })

    # === SCHRITT 4: Monatliche Reports generieren ===
    alle_monate = sorted([m for m in df_analyse['Monat'].unique() if m])

    for monat in alle_monate:
        monat_df = df_analyse[df_analyse['Monat'] == monat]
        monat_compact = monat.replace('-', '')

        rows = []
        sums = {k: 0.0 for k in ['miete', 'bkmi', 'bkhv', 'rep', 'energie']}

        for entry in geordnete_obids:
            obid = entry['OBID']
            objekttyp = entry['Objekttyp']
            obj_df = monat_df[monat_df['OBID'] == obid]

            miete = obj_df[obj_df['Buchungstyp'] == 'Miete']['Betrag'].sum()
            bk_mi, bk_hv_raw, ruwe = get_bk_ruwe(obj_df)
            bk_hv = bk_hv_raw + ruwe  # Rücküberweisung in BKHV einrechnen (netto)
            rep = obj_df[obj_df['Buchungstyp'] == 'Reparatur']['Betrag'].sum()
            energie = obj_df[obj_df['Buchungstyp'] == 'Energiekosten']['Betrag'].sum()

            # Diagnose: W/G (bzw. w/g bei Eigennutzung) + Leerzeichen + <, >, =
            diag = ''
            if round(bk_mi, 2) != 0 or round(bk_hv, 2) != 0:
                # Eigennutzung: IBAN des Mieters = Vermieter-IBAN → Kleinbuchstabe
                eigennutzung = False
                iban = entry.get('IBAN', '')
                if iban:
                    pi = tables['partner_table'].get(iban, {})
                    if pi.get('Typ') == 'Vermieter':
                        eigennutzung = True
                if objekttyp == 'Wohnung':
                    prefix = 'w' if eigennutzung else 'W'
                else:
                    prefix = 'g' if eigennutzung else 'G'
                bkmi_r = round(bk_mi, 2)
                bkhv_r = round(abs(bk_hv), 2)
                if bkmi_r < bkhv_r:
                    diag = f'{prefix} <'
                elif bkmi_r > bkhv_r:
                    diag = f'{prefix} >'
                else:
                    diag = f'{prefix} ='

            sums['miete'] += miete
            sums['bkmi'] += bk_mi
            sums['bkhv'] += bk_hv
            sums['rep'] += rep
            sums['energie'] += energie

            rows.append({
                'OBID': obid,
                'Mietername': entry['Mietername'],
                'Miete': miete,
                'BKMi': bk_mi,
                'BKHV': bk_hv,
                'Diag': diag,
                'Reparatur': rep,
                'Energie': energie,
            })

        # Summenzeile
        totals = {
            'OBID': 'SUMME', 'Mietername': '',
            'Miete': sums['miete'], 'BKMi': sums['bkmi'],
            'BKHV': sums['bkhv'], 'Diag': '',
            'Reparatur': sums['rep'], 'Energie': sums['energie'],
        }

        def fmt(val):
            if val == 0.0:
                return ''
            return f'{val:.2f}'

        # Spaltenreihenfolge: Diag vor Reparatur und Energie
        col_headers = ['OBID', 'Mietername', 'Miete', 'BKMi', 'BKHV', 'Diag', 'Reparatur', 'Energie']
        col_keys = ['OBID', 'Mietername', 'Miete', 'BKMi', 'BKHV', 'Diag', 'Reparatur', 'Energie']
        text_cols = {'OBID', 'Mietername', 'Diag'}
        num_cols_idx = {i for i, k in enumerate(col_keys) if k not in text_cols}

        # === Zusatzdaten für diesen Monat sammeln ===
        rep_rows = monat_df[monat_df['Buchungstyp'] == 'Reparatur'].sort_values('Valutadatum')
        kaut_rows = monat_df[monat_df['Buchungstyp'] == 'Kaution'].sort_values(['OBID', 'Valutadatum'])
        eigen_rows = monat_df[monat_df['Buchungstyp'] == 'Eigenentnahme'].sort_values('Valutadatum')

        # === TXT Output (Fixed-width) ===
        widths = [len(h) for h in col_headers]
        all_rows_txt = []
        for r in rows:
            vals = [r[k] if k in text_cols else fmt(r[k]) for k in col_keys]
            all_rows_txt.append(vals)
            for i, v in enumerate(vals):
                widths[i] = max(widths[i], len(str(v)))
        total_vals = [totals[k] if k in text_cols else fmt(totals[k]) for k in col_keys]
        total_vals[0] = 'SUMME'
        for i, v in enumerate(total_vals):
            widths[i] = max(widths[i], len(str(v)))

        def pad(val, width, idx):
            if idx in num_cols_idx:
                return str(val).rjust(width)
            return str(val).ljust(width)

        lines = []
        lines.append(f'Wohneinheiten-Übersicht {monat}')
        total_width = sum(widths) + 3 * (len(widths) - 1)
        lines.append('=' * total_width)
        lines.append('   '.join(pad(h, widths[i], i) for i, h in enumerate(col_headers)))
        lines.append('-' * total_width)
        for vals in all_rows_txt:
            lines.append('   '.join(pad(v, widths[i], i) for i, v in enumerate(vals)))
        lines.append('-' * total_width)
        lines.append('   '.join(pad(v, widths[i], i) for i, v in enumerate(total_vals)))

        # Reparaturen
        if not rep_rows.empty:
            lines.append('')
            lines.append('Reparaturen:')
            for _, rr in rep_rows.iterrows():
                kommentar = str(rr.get('Kommentar', ''))[:80]
                lines.append(f'  {rr["Valutadatum"]}  {rr["OBID"]:<10s}  {rr["Partnername"]:<35s}  {rr["Betrag"]:>10.2f}  {kommentar}')

        # Kautionen (gemeinsame Datenaufbereitung für TXT und MD)
        kaut_by_obid = {}
        if not kaut_rows.empty:
            for _, kr in kaut_rows.iterrows():
                obid_k = kr['OBID']
                if obid_k not in kaut_by_obid:
                    kaut_by_obid[obid_k] = {'mieter_name': '', 'mieter_betrag': 0.0,
                                             'vermieter_betrag': 0.0, 'vermieter_iban': '', 'vermieter_name': ''}
                pt = get_partnertyp(kr['Partner-IBAN'])
                if pt == 'Vermieter':
                    kaut_by_obid[obid_k]['vermieter_betrag'] += kr['Betrag']
                    kaut_by_obid[obid_k]['vermieter_iban'] = kr['Partner-IBAN']
                    kaut_by_obid[obid_k]['vermieter_name'] = kr['Partnername']
                else:
                    kaut_by_obid[obid_k]['mieter_name'] = kr['Partnername']
                    kaut_by_obid[obid_k]['mieter_betrag'] += kr['Betrag']

        if kaut_by_obid:
            lines.append('')
            lines.append('Kautionen:')
            max_name = max(len(kd['mieter_name']) for kd in kaut_by_obid.values())
            max_name = max(max_name, 10)
            for obid_k in sorted(kaut_by_obid.keys()):
                kd = kaut_by_obid[obid_k]
                mi_str = fmt(kd['mieter_betrag']) if kd['mieter_betrag'] != 0 else ''
                vm_str = fmt(kd['vermieter_betrag']) if kd['vermieter_betrag'] != 0 else ''
                vm_info = f'({kd["vermieter_iban"]} {vm_str})' if vm_str else ''
                lines.append(f'{obid_k:<10s} {kd["mieter_name"]:<{max_name}s} {mi_str:>9s}  {vm_info}')

        # Eigenentnahmen
        if not eigen_rows.empty:
            lines.append('')
            lines.append('Eigenentnahmen:')
            for _, er in eigen_rows.iterrows():
                lines.append(f'  {er["Valutadatum"]}  {er["Betrag"]:>10.2f}  {er["Partnername"]}')

        lines.append('')

        txt_path = f'out_{monat_compact}.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        # === MD Output (Markdown Table) ===
        md_lines = []
        md_lines.append(f'# Wohneinheiten-Übersicht {monat}')
        md_lines.append('')
        md_header = '| ' + ' | '.join(col_headers) + ' |'
        aligns = []
        for i, k in enumerate(col_keys):
            if k in ('OBID', 'Mietername'):
                aligns.append(':---')
            elif k == 'Diag':
                aligns.append(':---:')
            else:
                aligns.append('---:')
        md_align = '| ' + ' | '.join(aligns) + ' |'
        md_lines.append(md_header)
        md_lines.append(md_align)
        for r in rows:
            vals = [r[k] if k in text_cols else fmt(r[k]) for k in col_keys]
            md_lines.append('| ' + ' | '.join(str(v) for v in vals) + ' |')
        def fmt_bold(val):
            s = fmt(val)
            return f'**{s}**' if s else ''
        sum_vals_md = []
        for k in col_keys:
            if k == 'OBID':
                sum_vals_md.append('**SUMME**')
            elif k in text_cols:
                sum_vals_md.append('')
            else:
                sum_vals_md.append(fmt_bold(totals[k]))
        md_lines.append('| ' + ' | '.join(sum_vals_md) + ' |')

        # Reparaturen
        if not rep_rows.empty:
            md_lines.append('')
            md_lines.append('### Reparaturen')
            md_lines.append('')
            md_lines.append('| Datum | OBID | Betrieb | Betrag | Beschreibung |')
            md_lines.append('| :--- | :--- | :--- | ---: | :--- |')
            for _, rr in rep_rows.iterrows():
                kommentar = str(rr.get('Kommentar', ''))[:80]
                md_lines.append(f'| {rr["Valutadatum"]} | {rr["OBID"]} | {rr["Partnername"]} | {rr["Betrag"]:.2f} | {kommentar} |')

        # Kautionen (kaut_by_obid wurde oben bereits aufbereitet)
        if kaut_by_obid:
            md_lines.append('')
            md_lines.append('### Kautionen')
            md_lines.append('')
            md_lines.append('| OBID | Mieter | von/an Mieter | Vermieter-Konto (Betrag) |')
            md_lines.append('| :--- | :--- | ---: | :--- |')
            for obid_k in sorted(kaut_by_obid.keys()):
                kd = kaut_by_obid[obid_k]
                vm_info = f'{kd["vermieter_iban"]} ({fmt(kd["vermieter_betrag"])})' if kd['vermieter_betrag'] != 0 else ''
                md_lines.append(f'| {obid_k} | {kd["mieter_name"]} | {fmt(kd["mieter_betrag"])} | {vm_info} |')

        # Eigenentnahmen
        if not eigen_rows.empty:
            md_lines.append('')
            md_lines.append('### Eigenentnahmen')
            md_lines.append('')
            md_lines.append('| Datum | Betrag | Empfänger |')
            md_lines.append('| :--- | ---: | :--- |')
            for _, er in eigen_rows.iterrows():
                md_lines.append(f'| {er["Valutadatum"]} | {er["Betrag"]:.2f} | {er["Partnername"]} |')

        md_lines.append('')

        md_path = f'out_{monat_compact}.md'
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))

        print(f"  - {txt_path} und {md_path} erstellt")

    return alle_monate


def create_excel_output(df_analyse, df_summary, findings, tables):
    """
    Erstellt eine Excel-Datei mit mehreren Sheets:
    - Analyse: Detaillierte Buchungsanalyse
    - Summary: Zusammenfassungen
    - Monatsübersicht: Pivot-Tabelle Monat x OBID
    - Plausibilität: Auffälligkeiten
    """
    output_file = 'out_mieten.xlsx'

    header_font = Font(bold=True, color='FFFFFF', size=11)
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    warn_fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
    err_fill = PatternFill(start_color='FCE4EC', end_color='FCE4EC', fill_type='solid')
    pos_font = Font(color='006100')
    neg_font = Font(color='9C0006')
    thin_border = Border(
        bottom=Side(style='thin', color='D9D9D9')
    )

    def style_header(ws):
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')

    def auto_width(ws, max_width=40):
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value) if cell.value else ''
                max_len = max(max_len, len(val))
            ws.column_dimensions[col_letter].width = min(max_len + 3, max_width)

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Analyse
        cols_analyse = ['Valutadatum', 'Buchungstyp', 'Objekttyp', 'OBID', 'HVID', 'EVID',
                       'Partner-IBAN', 'Partnername', 'Betrag', 'Kommentar']
        df_a = df_analyse[cols_analyse].copy()
        df_a.to_excel(writer, sheet_name='Analyse', index=False)
        ws = writer.sheets['Analyse']
        style_header(ws)
        # Beträge formatieren
        for row in ws.iter_rows(min_row=2, min_col=9, max_col=9):
            for cell in row:
                if cell.value is not None:
                    cell.number_format = '#,##0.00'
                    if isinstance(cell.value, (int, float)):
                        cell.font = pos_font if cell.value >= 0 else neg_font
        auto_width(ws)

        # Sheet 2: Summary
        cols_summary = ['Titel', 'Dimension', 'Gruppierung1', 'Gruppierung2', 'Saldo',
                       'SummePositiveBeträge', 'SummeNegativeBeträge', 'AnzahlBuchungen']
        df_s = df_summary[cols_summary].copy()
        df_s.to_excel(writer, sheet_name='Summary', index=False)
        ws = writer.sheets['Summary']
        style_header(ws)
        for row in ws.iter_rows(min_row=2, min_col=5, max_col=7):
            for cell in row:
                if cell.value is not None:
                    cell.number_format = '#,##0.00'
        auto_width(ws)

        # Sheet 3: Monatsübersicht (Pivot: Monat x OBID → Saldo Miete + BK)
        pivot_data = []
        alle_obids = sorted(tables['obid_to_info'].keys())
        alle_monate = sorted(df_analyse['Monat'].unique())
        for monat in alle_monate:
            if not monat:
                continue
            row_data = {'Monat': monat}
            monat_df = df_analyse[df_analyse['Monat'] == monat]
            total_miete = 0
            total_bk = 0
            for obid in alle_obids:
                obj_df = monat_df[monat_df['OBID'] == obid]
                miete = obj_df[obj_df['Buchungstyp'] == 'Miete']['Betrag'].sum()
                bk = obj_df[obj_df['Buchungstyp'] == 'Betriebskosten']['Betrag'].sum()
                row_data[f'{obid} Miete'] = round(miete, 2) if miete != 0 else None
                row_data[f'{obid} BK'] = round(bk, 2) if bk != 0 else None
                total_miete += miete
                total_bk += bk
            row_data['TOTAL Miete'] = round(total_miete, 2)
            row_data['TOTAL BK'] = round(total_bk, 2)
            row_data['TOTAL Saldo'] = round(total_miete + total_bk, 2)
            pivot_data.append(row_data)

        df_pivot = pd.DataFrame(pivot_data)
        df_pivot.to_excel(writer, sheet_name='Monatsübersicht', index=False)
        ws = writer.sheets['Monatsübersicht']
        style_header(ws)
        for row in ws.iter_rows(min_row=2, min_col=2, max_col=ws.max_column):
            for cell in row:
                if cell.value is not None and isinstance(cell.value, (int, float)):
                    cell.number_format = '#,##0.00'
                    cell.font = pos_font if cell.value >= 0 else neg_font
        auto_width(ws, max_width=18)

        # Sheet 4: Plausibilität
        if findings:
            df_f = pd.DataFrame(findings)
            df_f.to_excel(writer, sheet_name='Plausibilität', index=False)
            ws = writer.sheets['Plausibilität']
            style_header(ws)
            # Farbliche Markierung nach Typ
            for row_idx in range(2, ws.max_row + 1):
                typ = ws.cell(row=row_idx, column=1).value
                fill = warn_fill
                if typ in ['Mögliche Doppelzahlung', 'Hoher Betrag']:
                    fill = err_fill
                for col_idx in range(1, ws.max_column + 1):
                    ws.cell(row=row_idx, column=col_idx).fill = fill
            auto_width(ws, max_width=80)

    return output_file


def analyze_mieten():
    """
    Hauptfunktion zur Analyse der Mietbuchungen.
    """
    print("=== Starte Analyse der Mietbuchungen ===\n")
    
    # 1. Lade partner.csv
    print("Lade partner.csv...")
    tables = load_partner_csv('partner.csv')
    print(f"  - {len(tables['partner_table'])} Partner geladen")
    print(f"  - {len(tables['obid_to_info'])} Objekte (OBIDs) gefunden")
    print(f"  - {len(tables['mieter_table'])} Mieter-Einträge gefunden\n")
    
    # 2. Verarbeite umsaetze.csv
    print("Verarbeite umsaetze.csv...")
    df_analyse = process_umsaetze('umsaetze.csv', tables)
    print(f"  - {len(df_analyse)} Buchungen verarbeitet\n")
    
    # 3. Schreibe out_analyse.csv
    print("Schreibe out_analyse.csv...")
    cols_analyse = ['Valutadatum', 'Buchungstyp', 'Objekttyp', 'OBID', 'HVID', 'EVID',
                   'Partner-IBAN', 'Partnername', 'Betrag', 'Kommentar']
    # Formatiere Beträge auf exakt 2 Nachkommastellen
    df_out = df_analyse[cols_analyse].copy()
    df_out['Betrag'] = df_out['Betrag'].apply(lambda x: f'{x:.2f}')
    # Stelle sicher, dass IDs als Strings ausgegeben werden (keine Umwandlung zu float)
    for col in ['OBID', 'HVID', 'EVID', 'Partner-IBAN']:
        df_out[col] = df_out[col].astype(str).replace('nan', '')
    df_out.to_csv('out_analyse.csv', sep=';', index=False,
                  encoding='utf-8', lineterminator='\n')
    print("  - out_analyse.csv erstellt\n")
    
    # 4. Erstelle Summary
    print("Erstelle out_summary.csv...")
    df_summary = create_summary(df_analyse)
    
    # 5. Schreibe out_summary.csv
    cols_summary = ['Titel', 'Dimension', 'Gruppierung1', 'Gruppierung2', 'Saldo',
                   'SummePositiveBeträge', 'SummeNegativeBeträge', 'AnzahlBuchungen']
    # Formatiere Beträge auf exakt 2 Nachkommastellen
    df_sum_out = df_summary[cols_summary].copy()
    for col in ['Saldo', 'SummePositiveBeträge', 'SummeNegativeBeträge']:
        df_sum_out[col] = df_sum_out[col].apply(lambda x: f'{x:.2f}')
    df_sum_out.to_csv('out_summary.csv', sep=';', index=False,
                      encoding='utf-8', lineterminator='\n')
    print("  - out_summary.csv erstellt\n")

    # 6. Monatliche Wohneinheiten-Übersicht
    print("Erstelle monatliche Wohneinheiten-Übersichten...")
    create_monthly_reports(df_analyse, tables)
    print()

    # 7. Plausibilitätsprüfung
    print("Plausibilitätsprüfung...")
    findings = plausibility_checks(df_analyse, tables)
    if findings:
        print(f"  - {len(findings)} Auffälligkeiten gefunden:")
        for f in findings:
            obid_str = f" [{f['OBID']}]" if f['OBID'] else ""
            print(f"    {f['Typ']}{obid_str}: {f['Detail']}")
    else:
        print("  - Keine Auffälligkeiten gefunden.")
    print()

    # 8. Excel-Output erstellen
    print("Erstelle Excel-Output...")
    excel_file = create_excel_output(df_analyse, df_summary, findings, tables)
    print(f"  - {excel_file} erstellt\n")

    print("=== Analyse erfolgreich abgeschlossen! ===")

if __name__ == "__main__":
    analyze_mieten()

