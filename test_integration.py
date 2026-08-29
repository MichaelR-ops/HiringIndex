import json
import sys
from src.parser import parse_html_job_count

def main():
    try:
        with open("config/companies.json", "r", encoding="utf-8") as f:
            companies = json.load(f)
        company_cfg = companies.get("a_raymond_gmbh_co_kg")
        if not company_cfg:
            print("Company config for a_raymond_gmbh_co_kg not found.")
            sys.exit(1)
        job_count = parse_html_job_count(company_cfg)
        print(f"Job count for {company_cfg.get('firma')}: {job_count}")
    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
