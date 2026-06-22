# RACI-VS Manager — Benutzeranleitung

## Inhalt

1. [Installation](#installation)
2. [Überblick](#überblick)
3. [Erste Schritte: neue Organisation anlegen](#erste-schritte-neue-organisation-anlegen)
4. [Organisation löschen](#organisation-löschen)
5. [Organisation importieren](#organisation-importieren)
6. [Funktionen anlegen und bearbeiten](#funktionen-anlegen-und-bearbeiten)
7. [Aufgaben anlegen und bearbeiten](#aufgaben-anlegen-und-bearbeiten)
8. [Rollen zuweisen](#rollen-zuweisen)
9. [Matrix ansehen](#matrix-ansehen)
10. [Organigramm](#organigramm)
11. [Schnittstelle zwischen zwei Funktionen](#schnittstelle-zwischen-zwei-funktionen)
12. [Dokumente: Vorschau und Download](#dokumente-vorschau-und-download)
13. [Organisation exportieren](#organisation-exportieren)

---

## Installation

Die App läuft vollständig ohne Python-Installation oder Terminal.

1. **Installer ausführen** — starte `RACI-VS_Setup.exe`. Windows zeigt möglicherweise eine **SmartScreen-Warnung** ("Windows hat den PC geschützt"), weil die App nicht mit einem kommerziellen Zertifikat signiert ist. Klicke in diesem Fall auf **Weitere Informationen** und dann auf **Trotzdem ausführen**. Danach folge dem Installationsassistenten. Die App wird standardmäßig im Benutzerverzeichnis installiert; Administratorrechte sind nicht erforderlich. Optional kann beim Setup eine Desktop-Verknüpfung erstellt werden.

2. **App starten** — öffne **RACI-VS Manager** über das Startmenü oder die Desktop-Verknüpfung. Der Server startet automatisch im Hintergrund und der Browser öffnet sich auf `http://127.0.0.1:8000`.

3. **Tray-Icon** — in der Windows-Taskleiste erscheint ein blaues RACI-VS-Symbol. Darüber lässt sich die App jederzeit im Browser öffnen (**Open RACI-VS**) oder vollständig beenden (**Quit**). Das Browserfenster selbst zu schließen stoppt die App *nicht* — der Server läuft weiter im Hintergrund.

4. **Daten** — die Datenbank (`raci_vs.db`) liegt im selben Ordner wie die `RACI-VS.exe`. Sie wird beim ersten Start automatisch angelegt. Beim Deinstallieren bleibt die Datenbank erhalten und muss bei Bedarf manuell gelöscht werden.

> **Fehlersuche:** Startet die App nicht oder zeigt der Browser eine Fehlermeldung, liegt die Logdatei `raci_vs.log` im selben Ordner wie `RACI-VS.exe` und enthält die Fehlermeldung.

---

## Überblick

Der RACI-VS Manager ist eine lokal laufende Web-App zur Verwaltung von Verantwortungsmatrizen. Funktionen (Stellen, Rollen im Unternehmen) und Aufgaben (Tätigkeiten, Prozesse) werden miteinander verknüpft, indem jeder Funktion für jede Aufgabe eine Rolle aus dem RACI-VS-Schema zugewiesen wird. Das Ergebnis lässt sich als Matrix anzeigen und als Word-Dokument exportieren.

**Navigation:** Die Menüleiste oben enthält die Bereiche **Matrix**, **Funktionen**, **Aufgaben**, **Schnittstelle** und **Organisation**. Links oben befindet sich der Organisations-Umschalter.

**App beenden:** In der Desktop-App-Version läuft der Server im Hintergrund — das Schließen des Browser-Tabs beendet die App nicht. Zum Beenden das **Tray-Icon** in der Taskleiste anklicken und **Quit** wählen.

---

## Erste Schritte: neue Organisation anlegen

Eine Organisation ist ein abgeschlossener Arbeitsbereich mit eigenen Funktionen, Aufgaben und Rollenzuweisungen. Mehrere Organisationen können parallel in der App existieren.

1. Klicke oben links auf den **Organisations-Umschalter** (zeigt den Namen der aktuell aktiven Organisation).
2. Ein Dropdown öffnet sich. Gib im Textfeld unten im Dropdown einen Namen für die neue Organisation ein.
3. Drücke **Enter** oder klicke die Schaltfläche zum Bestätigen.
4. Die neue, leere Organisation wird angelegt und sofort als aktive Organisation gesetzt.

> Die aktive Organisation bestimmt, welche Funktionen, Aufgaben und Matrizen angezeigt werden. Alle Aktionen (Anlegen, Bearbeiten, Löschen) wirken immer nur auf die aktive Organisation.

---

## Organisation löschen

Eine nicht mehr benötigte Organisation kann dauerhaft entfernt werden. Dabei werden alle zugehörigen Funktionen, Aufgaben und Rollenzuweisungen unwiderruflich gelöscht.

1. Klicke oben links auf den **Organisations-Umschalter** (zeigt den Namen der aktuell aktiven Organisation).
2. Klicke auf den **Namen der aktiven Organisation** (mit dem Häkchen ✓ markiert).
3. Es öffnet sich das Fenster **Organisationen verwalten**. Darin werden alle angelegten Organisationen aufgelistet.
4. Klicke bei der zu löschenden Organisation auf **Löschen** und bestätige die Sicherheitsabfrage.
5. Die Organisation verschwindet sofort aus der Liste.

> **Hinweis:** Die aktuell aktive Organisation (mit ✓ markiert) kann nicht gelöscht werden. Wechsle zuerst in eine andere Organisation, wenn du die aktive löschen möchtest. Ist nur eine einzige Organisation vorhanden, erscheint kein Löschen-Button.

---

## Organisation importieren

Statt von Grund auf neu zu beginnen, kann eine zuvor exportierte Organisation als `.json`-Datei importiert werden. Das Beispiel-Datenpaket (`examples/Beispiel-org.json`) im Repository eignet sich zum ersten Ausprobieren.

1. Klicke auf den **Organisations-Umschalter** oben links.
2. Klicke auf **↑ Organisation importieren (.json)**.
3. Wähle die `.json`-Datei in deinem Datei-Browser aus.
4. Die Datei wird sofort hochgeladen. Es wird eine neue Organisation mit allen Funktionen, Aufgaben und Rollenzuweisungen aus der Datei erstellt. Existiert bereits eine Organisation mit demselben Namen, wird automatisch ein Suffix angehängt (z. B. *MeineOrg (2)*).
5. Die importierte Organisation ist danach direkt die aktive.

---

## Funktionen anlegen und bearbeiten

Funktionen repräsentieren Stellen oder Rollen im Unternehmen (z. B. *Projektmanager*, *Entwickler*, *Stakeholder*).

### Neue Funktion anlegen

1. Klicke in der Navigation auf **Funktionen**.
2. Scrolle zum Bereich **Neue Funktion hinzufügen** (unterhalb der Tabelle, aufklappbar).
3. Fülle die Felder aus:
   - **Name** *(Pflichtfeld)* — eindeutiger Bezeichner der Funktion
   - **Übergeordnete Funktion** — ordnet die Funktion in die Unternehmenshierarchie ein; bleibt leer bei Funktionen auf oberster Ebene
   - **Notfallvertreter** — welche Funktion diese im Notfall vertritt
   - **Beschreibung** — was diese Funktion tut
   - **Ziel** — wozu diese Funktion existiert
   - **Befugnisse** — Zeichnungsberechtigungen oder Handlungsvollmachten (Freitext, z. B. *Zeichnungsberechtigung bis 50.000 EUR*)
4. Klicke **Funktion hinzufügen**. Die neue Funktion erscheint sofort in der Tabelle.

### Funktion bearbeiten

1. Klicke in der Funktionsliste auf den Namen der Funktion.
2. Scrolle auf der Detailseite zum Bereich **Funktion bearbeiten**.
3. Ändere die gewünschten Felder und klicke **Änderungen speichern**.

### Funktion löschen

In der Funktionsliste: klicke **Löschen** in der Zeile der Funktion. Es erscheint eine Sicherheitsabfrage. Das Löschen entfernt auch alle Rollenzuweisungen dieser Funktion.

---

## Aufgaben anlegen und bearbeiten

Aufgaben repräsentieren Tätigkeiten oder Prozesse (z. B. *Anforderung erfassen*, *Code schreiben*, *Freigabe erteilen*).

### Neue Aufgabe anlegen

1. Klicke in der Navigation auf **Aufgaben**.
2. Scrolle zum Bereich **Neue Aufgabe hinzufügen**.
3. Fülle die Felder aus:
   - **Titel** *(Pflichtfeld)* — kurze Bezeichnung der Aufgabe
   - **Beschreibung** — was bei dieser Aufgabe zu tun ist
4. Optional: Klicke **+ Funktion hinzufügen**, um bereits beim Anlegen Rollenzuweisungen zu erstellen. Es können beliebig viele Zeilen hinzugefügt werden; jede Zeile enthält eine Funktion und eine Rolle (bei Rolle **R** erscheint zusätzlich ein Unterkategorie-Dropdown).
5. Klicke **Aufgabe hinzufügen**.

### Aufgabe bearbeiten

1. Klicke in der Aufgabenliste auf den Titel der Aufgabe.
2. Scrolle zum Bereich **Aufgabe bearbeiten**, ändere Titel oder Beschreibung und klicke **Änderungen speichern**.

### Aufgabe löschen

In der Aufgabenliste: klicke **Löschen** in der Zeile der Aufgabe. Das Löschen entfernt auch alle Rollenzuweisungen dieser Aufgabe.

---

## Rollen zuweisen

### Die sechs Rollen

| Kürzel | Name | Bedeutung |
|---|---|---|
| R | Durchführungsverantwortlich | Führt die Aufgabe aus |
| A | Ergebnisverantwortlich | Trägt die Verantwortung für das Ergebnis |
| C | Beratend | Wird vorab konsultiert |
| I | Informiert | Wird über das Ergebnis informiert |
| V | Prüfend | Prüft das Ergebnis |
| S | Unterzeichnend | Zeichnet formal ab |

Jede Funktion kann pro Aufgabe genau eine Rolle innehaben.

Die Rolle **R** erfordert zusätzlich eine **Unterkategorie**:

| Unterkategorie | Bedeutung |
|---|---|
| Ausführende Tätigkeit | Direkte operative Ausführung |
| Gewährleistung | Sicherstellt, dass die Aufgabe erfüllt wird |
| Koordination | Koordiniert die Durchführung |
| Veranlassung | Beauftragt die Durchführung |
| Mitwirkung | Wirkt unterstützend mit |

### Zuweisung über die Funktionsdetailseite

1. Klicke auf eine Funktion → Detailseite öffnet sich.
2. Im Bereich **Aufgaben & Rollen** erscheint das Formular **Zuweisen**, sofern noch nicht alle Aufgaben zugewiesen sind.
3. Wähle eine **Aufgabe** und eine **Rolle**. Bei Rolle **R** erscheint ein drittes Dropdown für die Unterkategorie.
4. Klicke **Zuweisen**. Die neue Zeile erscheint sofort in der Tabelle.

### Zuweisung über die Aufgabendetailseite

Genauso funktioniert es von der anderen Seite: Aufgabe öffnen → **Funktion zuweisen**-Formular → Funktion und Rolle auswählen → **Zuweisen**.

### Zuweisung entfernen

In der Zuweis-Tabelle (Funktionsdetail oder Aufgabendetail): **Entfernen**-Schaltfläche in der entsprechenden Zeile klicken. Die Zeile wird sofort entfernt.

---

## Matrix ansehen

Die **Matrix**-Seite (Startseite, erreichbar über das Logo oder den Menüpunkt **Matrix**) zeigt alle Aufgaben und Funktionen der aktiven Organisation in einer Übersichtstabelle:

- **Zeilen** = Aufgaben
- **Spalten** = Funktionen
- **Zellen** = farbige Rollenbadges (R, A, C, I, V, S) für bestehende Zuweisungen

Die Matrix aktualisiert sich beim nächsten Laden automatisch. Leere Zellen bedeuten: diese Funktion hat für diese Aufgabe keine Rolle.

Solange keine Funktionen und Aufgaben angelegt sind, zeigt die Matrix einen Hinweis mit Links zu den entsprechenden Bereichen.

---

## Organigramm

Der Bereich **Organisation** (Navigation oben) zeigt alle Funktionen der aktiven Organisation als hierarchisches Baumdiagramm, basierend auf den eingetragenen übergeordneten Funktionen.

- Jedes Kästchen ist ein Link zur Detailseite der jeweiligen Funktion.
- Funktionen ohne übergeordnete Funktion erscheinen auf der obersten Ebene.
- Das Diagramm hilft dabei, die Unternehmensstruktur zu überprüfen und fehlende Hierarchieverbindungen zu erkennen.

---

## Schnittstelle zwischen zwei Funktionen

Der Bereich **Schnittstelle** zeigt, welche Aufgaben zwei ausgewählte Funktionen gemeinsam haben, und welche Rollen sie dabei jeweils einnehmen.

1. Klicke auf **Schnittstelle** in der Navigation.
2. Wähle **Funktion A** und **Funktion B** aus den Dropdowns.
3. Klicke **Schnittstelle anzeigen**.
4. Die Tabelle listet alle gemeinsamen Aufgaben mit den Rollen beider Funktionen auf.
5. Über **Download .docx** lässt sich ein Schnittstellendokument als Word-Datei herunterladen.

---

## Dokumente: Vorschau und Download

Für jede Funktion gibt es eine vollständige **Funktionsbeschreibung** als strukturiertes Dokument mit 10 Abschnitten:

1. Organisatorische Einordnung (über- und untergeordnete Funktionen)
2. Ziel der Funktion
3. Ergebnisverantwortung (A)
4. Durchführungsverantwortung (R) — aufgeteilt nach Unterkategorien
5. Beratungsverantwortung (C)
6. Informationsverantwortung (I)
7. Verifikationsverantwortung (V)
8. Signaturverantwortung (S)
9. Befugnisse
10. Vertretung

Abschnitte ohne Zuweisungen erhalten automatisch den Platzhaltertext *Details ergänzen*.

### Vorschau öffnen

Auf der Detailseite einer Funktion: Schaltfläche **Vorschau** → öffnet die Funktionsbeschreibung als formatierte HTML-Seite in einem neuen Tab.

Auf der Vorschauseite gibt es:
- **Drucken / PDF** — öffnet den Browser-Druckdialog; über *Als PDF speichern* lässt sich ein PDF erzeugen, ohne eine Datei herunterladen zu müssen.
- **Download .docx** — lädt das Dokument als Word-Datei herunter.

### Word-Dokument direkt herunterladen

Auf der Detailseite einer Funktion: Schaltfläche **Download .docx** → das Dokument wird sofort als `.docx`-Datei heruntergeladen (kompatibel mit Microsoft Word und LibreOffice).

Dasselbe gilt für Aufgaben und Schnittstellenberichte.

---

## Organisation exportieren

Der Export sichert die gesamte aktive Organisation (alle Funktionen, Aufgaben und Rollenzuweisungen) in einer einzelnen, menschenlesbaren `.json`-Datei.

1. Klicke auf den **Organisations-Umschalter** oben links.
2. Klicke auf **↓ Aktuelle Organisation exportieren**.
3. Der Browser lädt die Datei `<Organisationsname>_export.json` herunter.

Die Datei kann an Kolleginnen und Kollegen weitergegeben oder als Backup aufbewahrt werden und lässt sich jederzeit wieder importieren (siehe [Organisation importieren](#organisation-importieren)).
