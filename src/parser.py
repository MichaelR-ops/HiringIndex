"""Generic and company-specific job listing parsers."""

import re
import requests
from typing import Any, Callable, Dict, Mapping
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup


JobCountParser = Callable[[Mapping[str, Any]], int]


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


def parse_bite_job_count(config: Mapping[str, Any]) -> int:
    """Fetch a b-ite jobs API listing and return its total job count.

    The b-ite JobsApi (v1) is used by German employer career pages (e.g.
    ALB FILS KLINIKUM). A cross-origin fetch is accepted when the public
    listing API key and channel are sent in the JSON body.
    """
    target_url = config.get("url", None)
    if not isinstance(target_url, str) or not target_url:
        raise ValueError("No b-ite posting search URL configured")
    api_key = config.get("api_key", None)
    if not isinstance(api_key, str) or not api_key:
        raise ValueError("No b-ite api_key configured")

    response = requests.post(
        target_url,
        json={
            "key": api_key,
            "channel": config.get("channel", 0),
            "locale": config.get("locale", "de"),
            "sort": {"by": "custom.prio", "order": "asc"},
            "page": {"num": 1000},
            "filter": {},
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, Mapping):
        raise ValueError("b-ite response must be a JSON object")

    postings = data.get("jobPostings")
    page = data.get("page")
    if isinstance(page, Mapping) and isinstance(page.get("total"), int):
        total = page["total"]
    elif isinstance(postings, list):
        total = len(postings)
    else:
        raise ValueError("b-ite response does not contain a job count")
    if isinstance(total, bool) or not isinstance(total, int):
        raise ValueError("b-ite response does not contain an integer job count")
    if total < 0:
        raise ValueError("b-ite job count cannot be negative")
    return total


def parse_htmx_table_job_count(config: Mapping[str, Any]) -> int:
    """Count open positions behind htmx-loaded job tables (e.g. Django boards).

    Some career sites render the job list only after the page triggers an
    htmx POST to a ``load_path`` endpoint on load. The response is an HTML
    table whose ``<tbody>`` contains one row per posting. Unspecific rows
    (e.g. ``Initiativbewerber``) are skipped via the ``row_exclude`` regex.
    """
    page_urls = config.get("urls", None)
    if not isinstance(page_urls, list) or not page_urls:
        raise ValueError("htmx_table parser requires a list of career page URLs")
    load_path = config.get("load_path", "/de/job/load_jobs/")
    if not isinstance(load_path, str) or not load_path:
        raise ValueError("htmx_table parser load_path must be a non-empty string")
    row_exclude = config.get("row_exclude", None)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"})

    total = 0
    for page_url in page_urls:
        page = session.get(page_url, timeout=20)
        page.raise_for_status()
        html = page.text
        token_match = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"', html
        )
        loc_match = re.search(r'name="location_id" value="([0-9]+)"', html)
        if not token_match or not loc_match:
            raise ValueError("htmx_table page does not contain CSRF/location_id fields")

        parsed = urlparse(page_url)
        api_url = urlunparse((parsed.scheme, parsed.netloc, load_path, "", "", ""))
        response = session.post(
            api_url,
            data={"location_id": loc_match.group(1), "search": ""},
            headers={
                "Referer": page_url,
                "X-CSRFToken": token_match.group(1),
                "X-Requested-With": "XMLHttpRequest",
            },
            timeout=20,
        )
        response.raise_for_status()
        table = response.text
        tbody = re.search(r"<tbody>(.*?)</tbody>", table, flags=re.S)
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", tbody.group(1) if tbody else "", flags=re.S)
        for row in rows:
            if row_exclude and re.search(row_exclude, row, re.IGNORECASE):
                continue
            total += 1
    return total


def parse_link_count_job_count(config: Mapping[str, Any]) -> int:
    """Count open positions from links on a CMS career overview page.

    A CMS career page renders one link per open position (e.g. links whose
    slug contains ``stellenanzeigen_``). A configurable ``link_pattern``
    matches the per-position links and an optional ``exclude_pattern`` skips
    unspecific entries (e.g. ``initiativbewerbung``).
    """
    page_url = config.get("url", None)
    if not isinstance(page_url, str) or not page_url:
        raise ValueError("link_count parser URL must be a non-empty string")
    link_pattern = config.get("link_pattern", None)
    if not isinstance(link_pattern, str) or not link_pattern:
        raise ValueError("link_count parser requires a link_pattern regular expression")
    exclude_pattern = config.get("exclude_pattern", None)
    if exclude_pattern is not None and not isinstance(exclude_pattern, str):
        raise ValueError("link_count parser exclude_pattern must be a string")

    response = requests.get(
        page_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"},
        timeout=20,
    )
    response.raise_for_status()
    slugs = set(re.findall(link_pattern, response.text))
    if exclude_pattern:
        slugs = {
            slug
            for slug in slugs
            if not re.search(exclude_pattern, slug, re.IGNORECASE)
        }
    if not slugs:
        raise ValueError("link_count page does not contain any position links")
    return len(slugs)


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
