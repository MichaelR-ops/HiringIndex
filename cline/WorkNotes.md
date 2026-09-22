# WorkNotes – HiringIndex Handoff (2. md)

## Ziel (1 Zeile)
Für jede Firma aus `config/firmen.json` eine konfigurierte Job-Count-Extraktion in `config/companies.json` + nötige Parser in `src/parser.py`; verifiziert über `test_integration.py` (`COMPANY_KEY` = neuer Key). Siehe `cline/Orchestrator.md` (Delegation+Endkontrolle+Cleanup) und `cline/TaskAgent.md` (Executor-Loop).

## Fertige Firmen (verifizierte Counts)

| key | firma | parser | Count | Anmerkung |
|---|---|---|---|---|
| akkodis_germany | Akkodis Germany GmbH | html | 2009 | `typesenseJobCounts`-Regex (Next.js-SSR); DE-Portal, Sitemap unvollständig (925) |
| alb_fils_klinikum | ALB FILS KLINIKUM GmbH | bite | 56 | b-ite JobsApi v1 POST, `page.total` via public key+channel 0 |
| albert_ziegler_gmbh | Albert Ziegler GmbH | htmx_table | 44 | Django/htmx `load_jobs` je Standort: Giengen 40 (2 Initiativ abgezogen) + Rendsburg 4 |
| alexander_buerkle | Alexander Bürkle GmbH & Co. KG | link_count | 4 | CMS-Links `stellenanzeigen_*` minus Initiativbewerbung |

## Refactor 22.09.2026 (Parser-Abdeckung + Imports)
- Keine bestehenden Parser deckten b-ite-JSON, htmx/CSRF-Table-Boards oder Link-Matches ab; daher als **generische Plattform-Parser** umgesetzt:
  - `bite` → `parse_bite_job_count()` (wie workday/sap/brassring plattformgebunden, config: url/api_key/channel)
  - `ziegler` → **`htmx_table`** `parse_htmx_table_job_count()` (config: urls, load_path, row_exclude)
  - `buerkle` → **`link_count`** `parse_link_count_job_count()` (config: url, link_pattern, exclude_pattern)
- Alle `urllib.parse`-Imports von Funktions-Rumpf auf Modul-Ebene in `src/parser.py` gezogen; `JobCountParser`-Typhalias korrigiert.
- Registry (`pipeline.py`), `test_integration.py` PARSERS und `config/companies.json` auf neue Namen migriert.
| a_raymond_gmbh_co_kg | A. Raymond GmbH & Co. KG | html | 9 | careers.araymond.com (Drupal), `article.node-offer`; EN+DE identisch, global |
| agilent_technologies | Agilent Technologies Deutschland GmbH | workday | 360 | `agilent.wd5.myworkdayjobs.com/.../jobs` `total`; global, DE-Facet nicht verfügbar |
| abb_ag | ABB AG | html | 2103 | `"totalHits"`-Regex (SSR-JSON), careers.abb/dach/de/search-results |
| acps_automotive | ACPS Automotive GmbH | sap_successfactors | 16 | services/recruiting/v1/jobs |
| adk_gmbh | ADK GmbH für Gesundheit und Soziales | html | 65 | `div.joboffer_outer`, eine Seite, keine Pagination |
| adm_wild_europe | ADM WILD Europe GmbH & Co. KG | brassring | 575 | global/US-lastig (nur US-Site verfügbar) |
| aesculap_ag | Aesculap AG (B. Braun) | sap_successfactors | 253 | jobs.bbraun.com/services/recruiting/v1/jobs, de_DE-Default |

## Als Nächstes (Reihenfolge aus firmen.json, Key → bekannte Daten)
1. **Alfred Kärcher SE & Co. KG** – 16000 MA, „Eigenes Portal“ `https://careers.kaercher.com/` → Plattform prüfen.
2. **Amann & Söhne GmbH & Co. KG** – 2696 MA, keine URL.
3. **Amcor Flexibles Singen GmbH** – 48000 MA, Konzernportal `https://www.amcor.com/careers`.

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
