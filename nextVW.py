import requests
import re
from bs4 import BeautifulSoup


def vw_job_count(url: str) -> int:
    r = requests.get(
        url,
        params={"locale": "de_DE"},
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    r.raise_for_status()

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )

    label = soup.select_one(
        ".paginationLabel"
    )

    if not label:
        raise ValueError("Pagination nicht gefunden")

    text = label.get_text(
        " ",
        strip=True
    )

    # "Ergebnisse 1 – 25 von 97"
    m = re.search(
        r"von\s+(\d+)",
        text
    )

    if not m:
        raise ValueError(
            f"Keine Zahl in Pagination: {text}"
        )

    return int(m.group(1))


VW_URL = (
    "https://jobs.volkswagen-group.com/"
    "Volkswagen/search/"
    "?searchby=location"
    "&createNewAlert=false"
    "&q="
    "&locationsearch="
)


print(vw_job_count(VW_URL))