import requests
import re


url = "https://careers.dhl.com/eu/de/search-results?keywords="


html = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
).text


patterns = [
    r'"totalResults"\s*:\s*(\d+)',
    r'"totalResultsCount"\s*:\s*(\d+)',
    r'"totalCount"\s*:\s*(\d+)',
    r'"resultCount"\s*:\s*(\d+)',
    r'"jobCount"\s*:\s*(\d+)',
    r'"jobsCount"\s*:\s*(\d+)',
    r'"numberOfJobs"\s*:\s*(\d+)',
]


for p in patterns:
    hits = re.findall(
        p,
        html,
        re.I
    )

    print(
        p,
        "=>",
        hits[:10]
    )