# Sub‑Agenten‑Aufgabe – a_raymond_gmbh_co_kg

## Ziel
Ermittle die offizielle Karriere-/Job‑Seite von den Firmen in config/firmen.json sequentiell und liefere die Daten im nachfolgenden JSON‑Format. Ziel ist es im dem Skript HiringIDX.py die Anzahl der Stellenausschreibungen per Webscraping/API etc zu ermitteln. Im Kern soll eine Erweiterung der companies.json und falls nötig src/parser.py erfolgen, um mehr Firmen in den automatisierten HiringIDX aufzunehmen.

Lies zunächst das Projektverzeichnis, um den Kontext zu verstehen.

## Anforderungen
1. Quelle finden – prüfe Impressum, Footer‑Links, Sitemap und gängige Pfade (/jobs, /careers, /karriere). Die URL muss eindeutig der Firma zugeordnet sein.
2. Mitarbeiter‑Zahl – falls verfügbar, extrahiere die aktuelle Mitarbeiter‑Zahl. Nutze DE‑Angaben, sonst weltweit. Halte diese Recherche knapp - sie ist zweitrangig.
3. Parser‑Snippet – erweitere ggf. einen bestehenden Parser nur um das neue Endpoint‑Muster.
4. Input-JSON snippet:
```json
"A. Raymond GmbH & Co. KG" {
  "A. Raymond GmbH & Co. KG": {
    "employees": 1412,
    "industry": "Fahrzeugtechnik",
    "headquarter": "Lörrach"
  },
```
5. Ergebnis‑JSON – Beispiel:
```json
"a_raymond_gmbh_co_kg": {
  "firma": "A. Raymond GmbH & Co. KG",
  "industry": "Fahrzeugtechnik",
  "headquarter": "Lörrach",
  "mitarbeiter_zahl": 1412,
  "mitarbeiter_basis": "weltweit",
  "status": "completed",
  "parser": "html",
  "url": "<career‑url>"
}
```
6. Übertrag in companies.json, parser.py und den Status entsprechend anpassen.

## Regelwerk (Kurz)
1. Antworte kurz (< 150 Tokens).
2. Nutze vorhandene Bibliotheken.
3. Halte dich an das Projekt‑Schema.
4. Keine Parallelität – sequenziell.
5. Rate‑Limit‑Handler – max. 1 Request / 2 Sekunden pro Domain.
