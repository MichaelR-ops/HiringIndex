import json
import os
import sys
from src.parser import (
    parse_html_job_count,
    parse_workday_job_count,
    parse_sap_successfactors_job_count,
    parse_brassring_job_count,
    parse_bite_job_count,
    parse_htmx_table_job_count,
    parse_link_count_job_count,
)

PARSERS = {
    "html": parse_html_job_count,
    "workday": parse_workday_job_count,
    "sap_successfactors": parse_sap_successfactors_job_count,
    "brassring": parse_brassring_job_count,
    "bite": parse_bite_job_count,
    "htmx_table": parse_htmx_table_job_count,
    "link_count": parse_link_count_job_count,
}

COMPANY_KEY = os.environ.get("COMPANY_KEY", "alb_fils_klinikum")

def main():
    try:
        with open("config/companies.json", "r", encoding="utf-8") as f:
            companies = json.load(f)
        company_cfg = companies.get(COMPANY_KEY)
        if not company_cfg:
            print(f"Company config for {COMPANY_KEY} not found.")
            sys.exit(1)
        parser_name = company_cfg.get("parser", "html")
        parser = PARSERS.get(parser_name)
        if parser is None:
            print(f"No parser registered for {parser_name}")
            sys.exit(1)
        job_count = parser(company_cfg)
        print(f"Job count for {company_cfg.get('firma')}: {job_count}")
    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
