import requests
from bs4 import BeautifulSoup


BASE = (
    "https://jobs.volkswagen-group.com"
    "/Volkswagen/search/"
)


for offset in [0, 25, 50, 75]:

    params = {
        # "locale": "de_DE",
        # "searchby": "location",
        # "createNewAlert": "false",
        # "q": "",
        # "locationsearch": "",
        # "startrow": offset,
    }


    r = requests.get(
        BASE,
        params=params,
        headers={
            "User-Agent":
            "Mozilla/5.0"
        }
    )


    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    label = soup.select_one(
        ".paginationLabel"
    )


    print(
        offset,
        ":",
        label.get_text(
            " ",
            strip=True
        ) if label else "kein label"
    )