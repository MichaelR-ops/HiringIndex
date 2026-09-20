# Sub‑Agenten‑Aufgabe – a_raymond_gmbh_co_kg

## Ziel

### Zentrale Anweisung
Behalte die Anweisung, die offizielle Karriere‑/Job‑Seite zu finden, den Status zu aktualisieren und die URL in `companies.json` zu setzen, bei allen Schritten bei.
Ermittle die offizielle Karriere-/Job‑Seite von den Firmen in config/firmen.json sequentiell und liefere die Daten im nachfolgenden JSON‑Format. Ziel ist es im dem Skript HiringIDX.py die Anzahl der Stellenausschreibungen per Webscraping/API etc zu ermitteln. Im Kern soll eine Erweiterung der companies.json und falls nötig src/parser.py erfolgen, um mehr Firmen in den automatisierten HiringIDX aufzunehmen.

Lies zunächst das Projektverzeichnis, um den Kontext zu verstehen.

## Anweisungen Loop
1. Quelle finden – prüfe Impressum, Footer‑Links, Sitemap und gängige Pfade (/jobs, /careers, /karriere). Die URL muss eindeutig der Firma zugeordnet sein. Dein Ziel ist es die Karrierewebsite zu identifizieren und herauszufinden wie die Stellenanzahl automatisiert im Rahmen der Projektstruktur auslesbar ist oder auslesbar gemacht werden kann.
2. Mitarbeiter‑Zahl – falls verfügbar, extrahiere die aktuelle Mitarbeiter‑Zahl. Nutze vorrangig DE‑Angaben, ansonsten aber einfach weltweite Zahlen. Halte diese Recherche knapp - sie ist zweitrangig.
3. Parser‑Snippet – erweitere ggf. einen bestehenden Parser nur um das neue Endpoint‑Muster. Versuche wenn möglich bestehende Parser zu verwenden.
4. Input-JSON snippet:
```json
"Firma X" {
  "Firma X": {
    "employees": intEstimate,
    "industry": "industry type if available",
    "headquarter": "location"
  },
```
5. Ergebnis‑JSON – Beispiel:
```json
"Firma X": {
  "firma": "Firma X",
  "industry": "industry type if available",
  "headquarter": "location",
  "mitarbeiter_zahl": intEstimate,
  "mitarbeiter_basis": "weltweit ODER de",
  "status": "completed",
  "parser": "html",
  "url": "<career‑url>"
}
```
6. Übertrag in companies.json, parser.py und den Status entsprechend anpassen.

7. **Test‑Skript** – Nach dem Hinzufügen einer Firma führe ein kurzes Testskript aus, welches nur für diesen Eintrag das konfigurierte Scraping ausführt und den gefundenen Stellen‑Count ausgibt. Bearbeite hierfür test_integration.py durch das austauschen des Firmennamen. So wird die Extraktion sofort verifiziert, bevor du mit der nächsten Firma weiterarbeitest. NaN heißt, dass du gescheitert bist.

## Sonstige generelle Regeln

1. Antworte kurz (< 150 Tokens).
2. Nutze bevorzugt vorhandene Bibliotheken. Eine venv liegt im Projektordner vor. Sorge immer dafür, dass diese aktiviert ist und prüfe ob diese aktiv ist, wenn du Bibliotheken scheinbar nicht vorhanden sind
3. Halte dich an das Projekt‑Schema.
4. Keine Parallelität – sequenziell.
5. Rate‑Limit‑Handler – max. 1 Request / 2 Sekunden pro Domain.
6. Falls Bots unerwünscht sind, überspringe den Eintrag und gehe zur nächsten Firma über
