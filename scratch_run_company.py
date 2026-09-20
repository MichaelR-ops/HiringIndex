"""Scratch: run a specific registered parser for a company config."""
import json
import sys
from src.parser import parse_html_job_count, parse_workday_job_count, parse_sap_successfactors_job_count

PARSERS = {
    "html": parse_html_job_count,
    "workday": parse_workday_job_count,
    "sap_successfactors": parse_sap_successfactors_job_count,
}

company_key = sys.argv[1]
with open("config/companies.json", encoding="utf-8") as f:
    companies = json.load(f)
cfg = companies[company_key]
parser = PARSERS[cfg.get("parser", "html")]
count = parser(cfg)
print(f"COMPANY={company_key} FIRMA={cfg.get('firma')} PARSER={cfg.get('parser')} COUNT={count}")
