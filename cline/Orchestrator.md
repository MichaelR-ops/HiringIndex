# Orchestrator / Delegations-Template – HiringIndex

## Rollenmodell

- **Orchestrator** (dieses Dokument führt aus): steuert die Reihenfolge, delegiert einzelne Firmen an Executor-Agents, **kontrolliert jeden Executor separat** nach Abschluss und räumt auf.
- **Task Executor**: Bearbeitet **genau eine** Firma anhand von `cline/TaskAgent.md` (dort wird die aktuelle Firma eingetragen). Er PROBIERT und IMPLEMENTIERT nur, entscheidet aber nie über "fertig".
- Entscheidungsgewalt "completed" liegt ausschließlich beim Orchestrator nach seiner unabhängigen Kontrolle.

## Aktivität pro Firma

### 1) Delegieren (Orchestrator)
- Nächste Firma aus `config/firmen.json` (alphabetische Reihenfolge **der noch nicht in `companies.json` vorhandenen Firmen**).
- In `cline/TaskAgent.md` schreiben:
  - **Firma**, **Mitarbeiterzahl** (aus firmen.json), **bekannte career-URLs/-Software** (Workday/SF/BrassRing/…), **gewünschter `parser`**, wenn schon bekannt.
  - **Erfolgskriterium**: `test_integration.py` gibt eine positive ganzzahlige Jobanzahl aus (kein NaN, kein 0). Dafür muss dort `COMPANY_KEY` auf den neuen Key gesetzt werden.
- TaskAgent.md enthält die zentrale Loop-Anweisung bereits; Orchestrator ersetzt nur die Firmen-Sektion.

### 2) Ausführen (Task Executor) – kurz, sequenziell, <150 Tokens pro Antwort
- Plattform wie gehabt erkennen (Probe `scratch_probe.py`, Sitemap/Footer, /careers-/jobs-Pfade, Karriereportal).
- **Bevorzugt bestehende Parser** nutzen (Tabelle unten). Neuen Parser nur bei neuem Endpoint-Muster in `src/parser.py` ergänzen.
- Eintrag in `config/companies.json` anlegen, `notiz` mit Scope-Hinweis (nur DE / global / einschl. X).
- `test_integration.py`: `COMPANY_KEY` auf den neuen Key setzen und ausführen → Count im Konsolenoutput.
- Zwischenlösung protokollieren (nur 1 Zeile, z. B. "ABB: totalHits-Regex 2103"). **Keinen Status-Commit** setzen.

### 3) Separate Endkontrolle (Orchestrator – PFLICHT, eigene Sicht)
Nicht Ergebnis des Executors übernehmen, sondern unabhängig prüfen:
1. `python -m json.tool config/companies.json` → valide Syntax; Eintrag vollständig (firma, industry, headquarter, mitarbeiter_zahl, mitarbeiter_basis, parser, url, status, notiz).
2. Parser-Name im Registry-Default in `src/pipeline.py` (und ggf. `test_integration.py`) vorhanden.
3. `test_integration.py` **selbst ausführen**: Output zeigt positiven Integer > 0 (nicht bool/None).
4. **Kreuzcheck** (eine zweite, unabhängige Methode): z. B. API-Count vs. Anzahl Ergebnisseiten auf der Website, oder zweiter API-Pfad/Query-Variante. Weicht das stark ab (>10 %), Scope in `notiz` korrigieren und eine belegbare Zahl wählen.
5. Erst wenn 1–4 OK: `"status": "completed"` im Eintrag setzen.

### 4) Cleanup (PFLICHT nach erfolgreicher Implementierung)
- **Scratch-Skripte löschen**: alle Company-spezifischen Probes entfernen:
  `git clean -f 'scratch_*.py'` bzw. explizit `rm scratch_<firma>*.py scratch_br*.py scratch_abb*.py scratch_bbraun.py scratch_find_api.py scratch_hrefs.py scratch_grep.py`
- **Generische Utils BEHALTEN** (werden in `cline/WorkNotes.md` gelistet): `scratch_probe.py`, `scratch_run_company.py`, `scratch_save.py`.
- **Terminals schließen**: keine hängenden Prozesse zurücklassen; Kill-Fallback `pkill -f 'scratch_'`; laufende `run_commands` nie "offen" hinterlassen (immer `echo EXIT` + Timeout). VS-Code-Cline-Terminal-Panes der erledigten Sitzungen schließen.
- **Abschlusscheck**: `git status --short` zeigt nur die erwarteten Produktivdateien (config/companies.json, src/parser.py, src/pipeline.py, test_integration.py) – keine neuen `scratch_*`.

## Parser-Registry (Stand)

| parser | Endpoint/Methode | Beispiel |
|---|---|---|
| `html` | GET Seite + CSS-Selektor `selector` in config, Fallback: Regex `pattern` auf Roh-HTML (inkl. `<script>`-JSON) | ABB (`"totalHits"`), ADK (`div.joboffer_outer`) |
| `workday` | POST auf `{url}` mit `appliedFacets:{}, limit, offset,` → json `total` | Agilent | 
| `sap_successfactors` | POST `{url}` (= .../services/recruiting/v1/jobs) → json `totalJobs` | ACPS, Aesculap/B. Braun |
| `brassring` | GET Home (CSRF+Session), POST `…/TgNewUI/Search/Ajax/PowerSearchJobs` → `JobsCount` | ADM |

## Token-Sparregeln (Orchestrator + Executor)
- Antworten <150 Tokens; keine Kontext-Wiederholung; große Dateien nur gezielt (start/end_line) lesen.
- Unabhängige Reads/Checks gebündelt in einen Tool-Aufruf.
- Nach jedem Tool-Schritt sofort Ergebnis einordnen, keine Zwischen-Texte.
- Firmen-Reihenfolge und bekannte URLs stehen in `cline/WorkNotes.md` – nicht neu recherchieren.

## Betriebs-Fallstricke
- `curl` ist NICHT installiert → immer `requests`/`scratch_probe.py`.
- Terminal-Outputs können abgeschnitten sein (`...`); gezielt mit `grep`/`head` filtern.
- Rate-Limit: max. 1 Request/2 s pro Domain; bei Bot-Abwehr Firma überspringen (Executoren-Report vermerken).
