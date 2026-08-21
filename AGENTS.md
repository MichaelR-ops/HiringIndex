# HiringIndex: Arbeitsanweisung

## Zweck

Dieses Projekt liest Firmen- und Mitarbeiterdaten aus einer Excel-Datei, ruft die
Karriereseiten der Firmen ab, zählt offene Stellen und berechnet daraus den Hiring
Index. Die Ergebnisse werden in eine neue Excel-Datei geschrieben.

`Test_Struktur.xlsx` ist die Testeingabe und darf nicht verändert oder committed
werden. Die Ergebnisdatei ist `hiring_index.xlsx`.

## Arbeitsauftrag: Drei Unternehmen aus Baden-Württemberg

Die Firmenauswahl beginnt bei der regionalen Firmendatenbank:

<https://www.firmendatenbanken.de/firmen/n607/s/baden-wuerttemberg.html>

Arbeite zunächst genau drei Unternehmen aus Baden-Württemberg ab. Die Auswahl soll
praktikabel sein: Bevorzuge Unternehmen mit einer offiziellen Website, einer
erreichbaren Karriereseite und einer erkennbaren deutschen Stellenliste. Unternehmen
ohne Karriereseite werden dokumentiert, aber nicht künstlich konfiguriert.

Neue Firmen werden ausschließlich in dieser Tabelle eingetragen. Der Name muss exakt
dem Namen in `Test_Struktur.xlsx` entsprechen. `Initialer URL-Guess` darf zunächst
die Firmenprofil- oder Unternehmensseite aus der Datenbank sein.

| Firma | Initialer URL-Guess | Status |
| --- | --- | --- |
| Beispiel GmbH | https://www.beispiel.de/karriere | offen |
| Alfred Ritter GmbH & Co. KG | https://jobs.ritter-sport.com/search/?q=&locationsearch=&searchResultView=LIST | implementiert: 16 Stellen |
| MVZ AescuLabor-Karlsruhe GmbH | https://mvz-karlsruhe.career.softgarden.de/ | implementiert: 5 Stellen |

Aktualisiere den Status nach jedem Unternehmen mit einem kurzen, überprüfbaren
Ergebnis, zum Beispiel `implementiert: 12 Stellen`, `blockiert: keine
Karriereseite` oder `blockiert: Firmenbezug nicht verifizierbar`.

## Vorgehen für jedes der drei Unternehmen

1. Öffne den Firmeneintrag aus der BW-Datenbank und notiere den dort angegebenen
	Firmennamen, Ort und die offizielle Website.
2. Suche auf der offiziellen Website nach `Karriere`, `Jobs`, `Stellenangebote` oder
	entsprechenden deutschen Sprachvarianten. Folge internen Links, aber verwende keine
	Drittanbieter-Stellenbörse als Unternehmensseite, wenn keine Zuordnung belegbar ist.
3. Verifiziere die Beziehung zwischen Firma und Karriereseite über das Impressum:
	Vergleiche den vollständigen Firmennamen sowie, soweit vorhanden, Anschrift,
	Registerangaben oder Kontakt des verantwortlichen Unternehmens. Eine bloße
	Ähnlichkeit von Domainnamen reicht nicht aus. Dokumentiere bei Unklarheit den
	Status `blockiert` und konfiguriere die Firma nicht.
4. Ermittle bevorzugt deutsche Mitarbeiterzahlen. Verwende in dieser Reihenfolge:
	deutsche Mitarbeiterzahl der Firma, deutsche Mitarbeiterzahl des relevanten
	Standorts, belastbare Unternehmenszahl mit klarer Deutschland-Zuordnung, zuletzt
	`MA Weltweit` als Fallback. Verändere die Excel-Eingabe nicht; dokumentiere nur,
	welche Spalte als Basis verwendet wird.
5. Ermittle bevorzugt deutsche Stellenzahlen. Zähle nur aktive Stellen in Deutschland,
	sofern die Seite danach filtern kann. Zähle keine globalen Stellen zusätzlich und
	keine Presse-, Talentpool- oder Newsletter-Einträge. Ausbildungs-, Praktikums- und
	Werkstudentenstellen sind nur einzubeziehen, wenn sie im relevanten deutschen
	Stellenbereich gemeinsam mit regulären Stellen angezeigt werden; ansonsten separat
	prüfen und begründen.
6. Untersuche, ob die Stellenliste als serverseitiges HTML, eingebettete Daten oder
	API geliefert wird. Verwende zuerst bestehende Parser und Muster. Nutze stabile
	CSS-Selektoren für Jobkarten, Tabellenzeilen oder Ergebnisüberschriften und niemals
	feste Stellenzahlen.
7. Ergänze erst nach der Verifikation einen Eintrag in `config/companies.json`.
	Verwende den exakten Firmennamen aus der Excel-Datei, die firmenspezifische URL
	und den passenden vorhandenen Parser. Neue Bibliotheken oder eine neue Parser-
	Abstraktion benötigen vorherige Zustimmung.
8. Teste die Konfiguration live oder mit einem gespeicherten HTML-/API-Ausschnitt.
	Prüfe mindestens die erwartete positive Anzahl, die Deutschlandselektion und dass
	unerwünschte Bereiche nicht mitgezählt werden.
9. Führe einen kleinen Pipeline-Test mit Parser-Mock aus. Prüfe gemeinsam
	Mitarbeiterbasis, Stellenzahl und `hiring_index = job_count / employees`.
10. Prüfe die erzeugte Datei mit `pandas.read_excel`. Der Export muss eine echte
	`.xlsx`-Datei mit den Spalten `date`, `company`, `employees`, `job_count` und
	`hiring_index` sein.

## Bestehende technische Entscheidungen

- Als Mitarbeiterbasis wird `MA Weltweit` verwendet, weil `MA Deutschland` in der
  Testeingabe teilweise leer ist.
- Der Hiring Index ist `job_count / employees`.
- HTML-Stellenzähler werden über die Konfiguration in `config/companies.json` gesteuert.
  `selectors.job_count_rows` zählt passende Tabellenzeilen oder Jobkarten.
- Workday-Seiten verwenden den bestehenden `parse_workday_job_count` und ihre
  konfigurierte `jobs_api`.

## Regeln

- Keine Änderungen an Excel-Dateien committen.
- Jede neue Funktion braucht einen Docstring.
- Neue Bibliotheken nur nach vorheriger Zustimmung einführen.
- Der Ordner `scraps` enthält teilweise dysfunktionale Dateien und ist keine
  Testreferenz.
- Keine festen Stellenanzahlen in die Konfiguration eintragen.
- Vor jedem Commit Parser, Pipeline und Export mindestens fokussiert testen.

## Code-Stil

- Type Hints verwenden.
- Kleine Funktionen schreiben.
- Bestehende Parser und Konfigurationsmuster wiederverwenden.
- Globale Variablen vermeiden.
- Änderungen klein und auf die betreffende Firma bzw. den betreffenden Workflow
  beschränken.

## Technologie

- Python 3.14.6
- pandas
- requests
- BeautifulSoup