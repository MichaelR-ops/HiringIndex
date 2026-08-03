import re
import requests


def vw_job_count(url: str) -> int:
    params = {
        "locale": "de_DE"
    }

    r = requests.get(
        url,
        params=params,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    r.raise_for_status()

    m = re.search(
        r"von\s+(\d+)",
        r.text
    )

    if not m:
        raise ValueError("Keine Stellenanzahl gefunden")

    return int(m.group(1))