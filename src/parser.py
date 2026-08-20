"""Generic and company-specific job listing parsers."""

import re
import requests
from typing import Any, Callable, Dict, Mapping
from bs4 import BeautifulSoup
from .fetcher import fetch_career_page


JobCountParser = Callable[[str, Mapping[str, Any]], int]


def parse_html_job_count(url: str, config: Mapping[str, Any]) -> int:
    """Fetch an HTML career page and extract its configured job count."""
    page_url = config.get("url", url)
    if not isinstance(page_url, str) or not page_url:
        raise ValueError("HTML parser URL must be a non-empty string")
    return extract_job_count(fetch_career_page(page_url), dict(config))


def parse_workday_job_count(url: str, config: Mapping[str, Any]) -> int:
    """Fetch a Workday jobs API and return its total job count."""
    jobs_api = config.get("jobs_api", url)
    if not isinstance(jobs_api, str) or not jobs_api:
        raise ValueError("No Workday jobs API configured")
    response = requests.post(
        jobs_api,
        json={
            "appliedFacets": {},
            "limit": 20,
            "offset": 0,
            "searchText": ""
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "HiringIndex/1.0"
        },
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, Mapping):
        raise ValueError("Workday response must be a JSON object")

    total = data.get("total")
    if isinstance(total, bool) or not isinstance(total, int):
        raise ValueError("Workday response does not contain an integer total")
    if total < 0:
        raise ValueError("Workday job count cannot be negative")
    return total


def parse_sap_successfactors_job_count(
    url: str,
    config: Mapping[str, Any]
) -> int:
    """Fetch a SAP SuccessFactors jobs API and return its total job count."""
    jobs_api = config.get("jobs_api", url)
    if not isinstance(jobs_api, str) or not jobs_api:
        raise ValueError("No SAP SuccessFactors jobs API configured")
    response = requests.post(
        jobs_api,
        json={
            "locale": config.get("locale", "de_DE"),
            "pageNumber": 0,
            "sortBy": "",
            "keywords": "",
            "location": "",
            "facetFilters": {},
            "brand": "",
            "skills": [],
            "categoryId": 0,
            "alertId": "",
            "rcmCandidateId": ""
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "HiringIndex/1.0"
        },
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, Mapping):
        raise ValueError("SAP SuccessFactors response must be a JSON object")

    total = data.get("totalJobs")
    if isinstance(total, bool) or not isinstance(total, int):
        raise ValueError(
            "SAP SuccessFactors response does not contain an integer totalJobs"
        )
    if total < 0:
        raise ValueError("SAP SuccessFactors job count cannot be negative")
    return total


def extract_job_count(
    soup: BeautifulSoup,
    config: Dict[str, Any]
) -> int:
    """
    Extract job count from HTML using configuration-based selectors and patterns.
    
    This is a generic parser that works for any company by using configuration
    with CSS selectors and regex patterns provided in companies.json.
    
    Args:
        soup: BeautifulSoup parsed HTML
        config: Parser configuration with selectors and patterns for the company
        
    Returns:
        Number of open job positions
        
    Raises:
        ValueError: If job count cannot be extracted
    """
    selectors = config.get("selectors", {})
    patterns = config.get("patterns", {})

    count_selector = selectors.get("job_count_rows")
    if count_selector:
        rows = soup.select(count_selector)
        if not rows:
            raise ValueError(
                f"No job rows found with selector: {count_selector}"
            )
        return len(rows)
    
    selector = selectors.get("job_count")
    if not selector:
        raise ValueError("No job_count selector configured")
    
    # Support both single selector (string) and multiple selectors (list)
    selector_list = selector if isinstance(selector, list) else [selector]
    
    text = None
    for single_selector in selector_list:
        element = soup.select_one(single_selector)
        if element:
            text = element.get_text(" ", strip=True)
            break
    
    if not text:
        raise ValueError(
            f"Element not found with selectors: {selector_list}"
        )
    
    pattern = patterns.get("job_count")
    if not pattern:
        raise ValueError("No job_count pattern configured")
    
    # Find all matches using the configured regex pattern
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    if not matches:
        raise ValueError(f"No job count found in text: {text}")
    
    # Extract numbers from matches (handle both single and multiple capture groups)
    numbers = []
    for match in matches:
        if isinstance(match, tuple):
            # Multiple groups: take first non-empty group that looks like a number
            for group in match:
                if group and str(group).isdigit():
                    numbers.append(int(group))
        elif isinstance(match, str) and match.isdigit():
            numbers.append(int(match))
    
    if not numbers:
        raise ValueError(f"Could not extract number from pattern matches: {matches}")
    
    # Return the largest number (typically the total job count)
    return max(numbers)
