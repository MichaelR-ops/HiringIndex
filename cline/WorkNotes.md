# WorkNotes – HiringIndex Handoff (2. md)

## Ziel (1 Zeile)
Für jede Firma aus `config/firmen.json` eine konfigurierte Job-Count-Extraktion in `config/companies.json` + nötige Parser in `src/parser.py`; verifiziert über `test_integration.py` (`COMPANY_KEY` = neuer Key). Siehe `cline/Orchestrator.md` (Delegation+Endkontrolle+Cleanup) und `cline/TaskAgent.md` (Executor-Loop).

## Fertige Firmen (verifizierte Counts)

| key | firma | parser | Count | Anmerkung |
|---|---|---|---|---|
| abb_ag | ABB AG | html | 2103 | `"totalHits"`-Regex (SSR-JSON), careers.abb/dach/de/search-results |
| acps_automotive | ACPS Automotive GmbH | sap_successfactors | 16 | services/recruiting/v1/jobs |
| adk_gmbh | ADK GmbH für Gesundheit und Soziales | html | 65 | `div.joboffer_outer`, eine Seite, keine Pagination |
| adm_wild_europe | ADM WILD Europe GmbH & Co. KG | brassring | 575 | global/US-lastig (nur US-Site verfügbar) |
| aesculap_ag | Aesculap AG (B. Braun) | sap_successfactors | 253 | jobs.bbraun.com/services/recruiting/v1/jobs, de_DE-Default |

## Als Nächstes (Reihenfolge aus firmen.json, Key → bekannte Daten)
1. **Agilent Technologies Deutschland GmbH** – 15500 MA, Workday! API-URL vorhanden: `https://agilent.wd5.myworkdayjobs.com/wday/cxs/agilent/Agilent_Careers/jobs` → `workday`-Parser (Achtung: Deutschlandfilter? erst global zählen, Scope in notiz). Firma laut TaskAgent-Name aus Kontext: "Agilent Technologies Sales & Services GmbH & Co. KG" (1050).
2. **Akkodis Germany GmbH** – 5700 MA, "Eigenes Portal" `https://karriere.akkodis.com/` → vermutlich Html/JS.
3. **ALB FILS KLINIKUM GmbH** – 2485 MA, keine URL bekannt → Karriereseite googeln (klinik.de-Footer/Jobs).
4. **Albert Ziegler GmbH** – 1200 MA, keine URL.
5. **Alexander Bürkle GmbH & Co. KG** – 1169 MA, keine URL.

## Plattform-Muster (bei kombinierten Konzernseiten zuerst prüfen)
- **ABB**: careers.abb (ServiceNow/SSR) → Regex auf Timeline/JSON-Feld im HTML.
- **Workday**: POST `https://<tenant>.wd<X>.myworkdayjobs.com/wday/cxs/<org>/…/jobs` body `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}` → `total`.
- **SAP SuccessFactors**: POST `…/services/recruiting/v1/jobs` body laut `parse_sap_successfactors_job_count` → `totalJobs`.
- **BrassRing**: CSRF+Session aus Home-Seite, POST `…/TgNewUI/Search/Ajax/PowerSearchJobs` → `JobsCount`.
- Electron: careers „x" → Footer/Linker „Alle Stellen" folgen; Sitemap `…/sitemap.xml`.

## Verbleibende generische Utils (nicht löschen)
`scratch_probe.py <url> <tiefe>` (URL-Handshake+Hrefs), `scratch_run_company.py` (einen companies.json-Eintrag ausführen), `scratch_save.py` (HTML dumpen).

## Cleanup-Standard
Nach jeder erfolgreichen Firma: `.gitignore`-Stil `git clean -f 'scratch_*.py'` für Company-Probes (Utils behalten), hängende Prozesse killen, `git status` auf erwartete Mutationsdateien prüfen. Kein curl (nicht installiert): immer requests.
