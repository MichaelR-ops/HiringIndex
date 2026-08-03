import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de,en-US;q=0.9,en;q=0.8",
})

# Schritt 2: Jetzt erst die eigentliche Suche mit denselben Session-Cookies
url = "https://jobs.volkswagen-group.com/Volkswagen/search/"
params = {
    "searchby": "location",
    "createNewAlert": "false",
    "q": "",
    "locationsearch": "",
    "geolocation": "",
    "optionsFacetsDD_city": "",
    "optionsFacetsDD_facility": "",
    "optionsFacetsDD_department": "",
    "optionsFacetsDD_customfield2": "",
    "optionsFacetsDD_shifttype": "",
    "optionsFacetsDD_customfield3": "",
}

r = session.get(url, params=params, timeout=30)
print(r.url)
print(r.status_code)

soup = BeautifulSoup(r.text, "html.parser")
label = soup.select_one(".paginationLabel")
print(label.get_text(" ", strip=True) if label else "kein Label")