"""Test script for parser functionality with live career pages."""

from src.fetcher import fetch_career_page
from src.parser import extract_job_count
from src.config import load_company_config, get_company_parser_config


def test_vw_parser() -> None:
    """Test VW parser with live career page."""
    print("Testing VW Parser (live)...")
    try:
        url = "https://jobs.volkswagen-group.com/search/?searchby=location&createNewAlert=false&q=&locationsearch=&geolocation=&optionsFacetsDD_city=&optionsFacetsDD_facility=&optionsFacetsDD_department=&optionsFacetsDD_customfield2=&optionsFacetsDD_shifttype=&optionsFacetsDD_customfield3="
        
        config = load_company_config("config/companies.json")
        vw_config = config["volkswagen_ag"]
        
        soup = fetch_career_page(url)
        job_count = extract_job_count(soup, vw_config)
        print(f"  ✓ Successfully extracted {job_count} jobs from VW page")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_dhl_parser() -> None:
    """Test DHL parser with live career page."""
    print("Testing DHL Parser (live)...")
    try:
        url = "https://careers.dhl.com/eu/de/search-results?keywords="
        
        config = load_company_config("config/companies.json")
        dhl_config = config["deutsche_post_dhl"]
        
        soup = fetch_career_page(url)
        job_count = extract_job_count(soup, dhl_config)
        print(f"  ✓ Successfully extracted {job_count} jobs from DHL page")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Parser Tests with Live Career Pages")
    print("=" * 60)
    print()
    
    vw_ok = test_vw_parser()
    dhl_ok = test_dhl_parser()
    
    print()
    print("=" * 60)
    if vw_ok and dhl_ok:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed - see errors above")
