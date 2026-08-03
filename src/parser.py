"""Generic and company-specific job listing parsers."""

import re
from typing import Dict, Any, Optional, Union, List
from bs4 import BeautifulSoup


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
