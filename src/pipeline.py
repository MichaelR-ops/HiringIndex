"""Main processing pipeline for hiring index calculation."""

from datetime import datetime
from typing import Any, Dict, List, Mapping
from pathlib import Path
import pandas as pd

from .parser import (
    JobCountParser,
    parse_html_job_count,
    parse_workday_job_count,
    parse_sap_successfactors_job_count,
)
from .calculator import calculate_hiring_index
from .config import load_company_config


def process_companies(
    config_path: str = "config/companies.json",
    parser_registry: Mapping[str, JobCountParser] | None = None
) -> pd.DataFrame:
    """
    Process all companies and calculate hiring indices.
    
    Args:
        config_path: Path to company configuration file
        parser_registry: Mapping of parser names to parser implementations
        
    Returns:
        DataFrame with results including date, company, job count, and hiring index
    """
    # Resolve config path relative to project root
    config_file = Path(config_path)
    if not config_file.is_absolute():
        config_file = Path(__file__).parent.parent / config_path
    
    config = load_company_config(str(config_file))
    parsers = parser_registry or {
        "html": parse_html_job_count,
        "workday": parse_workday_job_count,
        "sap_successfactors": parse_sap_successfactors_job_count
    }
    results: List[Dict[str, Any]] = []

    for company_config in config.values():
        company_name = company_config.get("firma")
        career_url = company_config.get("url")
        employees = company_config.get("mitarbeiter_zahl")

        if not company_name or not career_url or employees is None:
            print(f"Skipping incomplete company configuration: {company_name or '<unknown>'}")
            continue

        print(f"Processing {company_name}...")

        try:
            parser_name = company_config.get("parser", "html")
            parser = parsers.get(parser_name)
            if parser is None:
                raise ValueError(f"No parser registered for {parser_name}")
            job_count = parser(career_url, company_config)
            print(f"  Jobs found: {job_count}")
            
            # Calculate hiring index
            hiring_index = calculate_hiring_index(job_count, employees)
            print(f"  Hiring Index: {hiring_index:.6f}")
            
            results.append({
                "date": datetime.today().date(),
                "company": company_name,
                "employees": employees,
                "job_count": job_count,
                "hiring_index": hiring_index
            })
            
        except Exception as e:
            print(f"  ERROR: {e}")
            # Still add a result row with null job count for tracking
            results.append({
                "date": datetime.today().date(),
                "company": company_name,
                "employees": employees,
                "job_count": None,
                "hiring_index": None
            })
    
    return pd.DataFrame(results)
