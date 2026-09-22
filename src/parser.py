"""Generic and company-specific job listing parsers."""

import re
import requests
from typing import Any, Callable, Dict, Mapping
from bs4 import BeautifulSoup


JobCountParser = Callable[[str, Mapping[str, Any]], int]


def parse_html_job_count(config: Mapping[str, Any]) -> int:
    """Fetch an HTML career page and extract its configured job count."""
    page_url = config.get("url", None)
    if not isinstance(page_url, str) or not page_url:
        raise ValueError("HTML parser URL must be a non-empty string")
    response = requests.get(
        page_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        },
        timeout=10,
    )
    response.raise_for_status()
    page = BeautifulSoup(response.text, "html.parser")
    return extract_job_count(page, dict(config))


def parse_workday_job_count(config: Mapping[str, Any]) -> int:
    """Fetch a Workday jobs API and return its total job count."""
    target_url = config.get("url", None)
    if not isinstance(target_url, str) or not target_url:
        raise ValueError("No Workday URL configured")
    response = requests.post(
        target_url,
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


def parse_sap_successfactors_job_count(config: Mapping[str, Any]) -> int:
    """Fetch a SAP SuccessFactors jobs API and return its total job count."""
    target_url = config.get("url", None)
    if not isinstance(target_url, str) or not target_url:
        raise ValueError("No SAP SuccessFactors URL configured")
    response = requests.post(
        target_url,
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

def parse_smart_recruiters_job_count(config: Mapping[str, Any]) -> int:
    """Fetch a SmartRecruiters postings API and return its total job count."""
    target_url = config.get("url", None)
    if not isinstance(target_url, str) or not target_url:
        raise ValueError("No SmartRecruiters URL configured")
    response = requests.get(
        target_url,
        params={"limit": 1, "offset": 0},
        headers={
            "Accept": "application/json",
            "User-Agent": "HiringIndex/1.0"
        },
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, Mapping):
        raise ValueError("SmartRecruiters response must be a JSON object")

    total = data.get("totalFound")
    if isinstance(total, bool) or not isinstance(total, int):
        raise ValueError(
            "SmartRecruiters response does not contain an integer totalFound"
        )
    if total < 0:
        raise ValueError("SmartRecruiters job count cannot be negative")
    return total

def parse_brassring_job_count(config: Mapping[str, Any]) -> int:
    """Fetch a BrassRing (IBM Kenexa) career portal job count.

    BrassRing career portals render the job list client-side. The count is
    fetched via a two-step flow:

    1. GET the search Home page and collect the ASP.NET session cookies,
       the CSRF token (``__RequestVerificationToken``) and the hidden partner/
       site/CookieValue fields.
    2. POST to ``/TgNewUI/Search/Ajax/PowerSearchJobs`` (relative to the Home
       URL host) with an empty keyword search and read ``JobsCount`` from the
       JSON response.
    """
    page_url = config.get("url", None)
    if not isinstance(page_url, str) or not page_url:
        raise ValueError("BrassRing parser URL must be a non-empty string")

    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "HiringIndex/1.0",
    }

    home_response = session.get(
        page_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        },
        timeout=20,
    )
    home_response.raise_for_status()
    home_html = home_response.text

    def hidden_value(name, attr="id"):
        pattern = re.compile(
            re.escape(attr) + r'="' + re.escape(name) + r'"[^>]*value="([^"]*)"'
        )
        match = pattern.search(home_html)
        if not match:
            pattern = re.compile(
                r'name="' + re.escape(name) + r'"[^>]*value="([^"]*)"'
            )
            match = pattern.search(home_html)
        return match.group(1) if match else ""

    partner_id = hidden_value("partnerId")
    site_id = hidden_value("siteId")
    cookie_value = hidden_value("CookieValue")
    if not partner_id or not site_id:
        raise ValueError(
            "BrassRing response does not contain hidden partnerId/siteId fields"
        )

    csrf_pattern = re.compile(
        r'name="__RequestVerificationToken"[^>]*value="([^"]*)"'
    )
    csrf_match = csrf_pattern.search(home_html)
    if not csrf_match:
        raise ValueError(
            "BrassRing response does not contain a CSRF token"
        )

    from urllib.parse import urljoin, urlparse

    api_url = "https://" + urlparse(page_url).netloc
    api_url = urljoin(api_url, "/TgNewUI/Search/Ajax/PowerSearchJobs")

    payload = {
        "PartnerId": partner_id,
        "SiteId": site_id,
        "Keyword": "",
        "Location": "",
        "KeywordCustomSolrFields": None,
        "LocationCustomSolrFields": None,
        "TurnOffHttps": False,
        "Latitude": 0,
        "Longitude": 0,
        "FacetFilterFields": {"Facet": None},
        "PowerSearchOptions": {"PowerSearchOption": None},
        "SortType": "",
        "EncryptedSessionValue": cookie_value,
        "PageIndex": 1,
        "ItemsPerPage": 10,
    }
    search_response = session.post(
        api_url,
        json=payload,
        headers={**headers, "RFT": csrf_match.group(1)},
        timeout=20,
    )
    search_response.raise_for_status()
    data = search_response.json()
    if not isinstance(data, Mapping):
        raise ValueError("BrassRing response must be a JSON object")

    total = data.get("JobsCount")
    if isinstance(total, bool) or not isinstance(total, int):
        raise ValueError(
            "BrassRing response does not contain an integer JobsCount"
        )
    if total < 0:
        raise ValueError("BrassRing job count cannot be negative")
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
    pattern = patterns.get("job_count")

    text = None
    if selector:
        # Support both single selector (string) and multiple selectors (list)
        selector_list = selector if isinstance(selector, list) else [selector]

        for single_selector in selector_list:
            element = soup.select_one(single_selector)
            if element:
                text = element.get_text(" ", strip=True)
                break

    if text is None and pattern:
        # Fallback: apply the regex pattern to the raw HTML source.
        # Covers SSR/embedded script JSON (e.g. Phenom People totalHits).
        text = str(soup)

    if not text:
        raise ValueError(
            f"Element not found with selectors: {selector}"
            if selector
            else "No job_count selector configured"
        )

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
