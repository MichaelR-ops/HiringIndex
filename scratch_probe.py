"""Scratch: probe a career page for job links, counts and JSON/API hints."""
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"


def probe(url, tag=None, sleep=2.0):
    if tag:
        time.sleep(sleep)
    h = {"User-Agent": UA}
    try:
        r = requests.get(url, headers=h, timeout=20, allow_redirects=True)
        print("INPUT_URL :", url)
        print("FINAL_URL :", r.url)
        print("STATUS    :", r.status_code)
        ctype = r.headers.get("Content-Type", "")
        print("CONTENT-TP:", ctype)
        if "html" not in ctype.lower():
            print("BODY-PREVIEW:", r.text[:800].replace("\n", " "))
            return
        soup = BeautifulSoup(r.text, "html.parser")
        seen = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            txt = a.get_text(" ", strip=True)[:60]
            low = (href + " " + txt).lower()
            if any(k in low for k in ["job", "stelle", "career", "vakanz", "open", "bewerb"]):
                full = urljoin(r.url, href)
                key = full.split("?")[0]
                if key in seen:
                    continue
                seen.add(key)
                print(f"LINK [{txt}] -> {full[:160]}")
        text = soup.get_text(" ")
        res = re.findall(r"(\d[\d.,' ]{0,6})\s*(offene\s+)?(Stellen|Jobs|Positionen|Vakanzen|Open(ings| Positions)|job listings)", text, re.I)
        if res:
            print("COUNT-HITS:", res[:10])
        # JSON-blocks / scripts
        for sc in soup.find_all("script"):
            s = sc.string or ""
            if re.search(r"(\bjobCount\b|totalJobs|listingCount|vacancies|\d+)\s*[:=]", s):
                for m in re.finditer(r"[{][^{}]{0,400}(totalJobs|jobCount|listingCount|vacancies)[^{}]{0,400}[}]", s, re.I):
                    print("JSON-HIT  :", m.group(0)[:500])
        for fx in ["jobCount", "totalJobs", "listingCount", "vacancies", "openPositions"]:
            for m in re.finditer(r"([\w.]*\b" + fx + r"[\w.]*)\s*[:=]\s*(\d+)", text, re.I):
                print("VAR-HIT   :", m.group(1), "=", m.group(2))
    except Exception as e:
        print("ERROR     :", url, e)


if __name__ == "__main__":
    url = sys.argv[1]
    sleep = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    probe(url, sleep=sleep)
