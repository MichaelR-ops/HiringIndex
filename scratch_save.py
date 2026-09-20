"""Scratch: save page and grep for API endpoints / embedded JSON."""
import re
import sys
import requests
from bs4 import BeautifulSoup

url = sys.argv[1]
out = sys.argv[2]
h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}
r = requests.get(url, headers=h, timeout=20, allow_redirects=True)
open(out, "w", encoding="utf-8").write(r.text)
print("FINAL:", r.url, r.status_code, "len:", len(r.text))
for m in re.finditer(r'/api/[^"\'\s<>]{2,120}', r.text):
    print("API:", m.group(0)[:150])
for m in re.finditer(r'(?:src|href)=["\']([^"\']*(?:vue|bundle|app|main|chunk)[^"\']*)["\']', r.text, re.I):
    print("ASSET:", m.group(1)[:150])
for m in re.finditer(r'window\.__[A-Z]+__\s*=\s*', r.text):
    print("WINDOW-JSON found")
for m in re.finditer(r'("(?:total|count|numFound|resultCount|hits)"\s*:\s*\d+)', r.text):
    print("COUNT-JSON:", m.group(1)[:120])
