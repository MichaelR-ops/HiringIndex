import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

# =========================
# CSV IO
# =========================

def load_companies(path: str) -> pd.DataFrame:
    ext = Path(path).suffix.lower()

    if ext == ".csv":
        return pd.read_csv(path)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"Nicht unterstütztes Dateiformat: {ext}")


def save_hiring_index(df: pd.DataFrame, path: str) -> None:
    """Speichert aktualisierte Hiring-Index-Historie."""
    df.to_csv(path, index=False)


# =========================
# Web Request
# =========================

def fetch_career_page(url: str) -> str:


    response = requests.get(
        url,
        # params={"locale": "de_DE"},
        headers={"User-Agent": "Mozilla/5.0"}
    )

    response.raise_for_status()

    soup = BeautifulSoup(
    response.text,
    "html.parser"
    )

    return soup


# =========================
# Parsing
# =========================

def extract_job_count(
    company: str,
    soup: str
) -> int:
    """
    Unternehmensspezifische Logik.

    Placeholder.
    """
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


# =========================
# Hiring Index
# =========================

def calculate_hiring_index(
    job_count: int,
    employee_count: int
) -> float:

    if employee_count == 0:
        return 0

    return job_count / employee_count


# =========================
# Main Processing
# =========================

def process_companies(
    companies_df: pd.DataFrame
) -> pd.DataFrame:

    results = []

    for _, row in companies_df.iterrows():

        company = row["Unternehmen"]
        url = row["Karriere-URL"]
        employees = row["MA Deutschland"]

        print(f"Processing {company}")

        try:

            raw_content = fetch_career_page(url)
            
            job_count = extract_job_count(
                company,
                raw_content
            )
            print(f"Jobs {company}: ",job_count)
            hiring_index = calculate_hiring_index(
                job_count,
                employees
            )

            print("Hiring Index:", hiring_index)

            results.append({
                "date": datetime.today().date(),
                "company": company,
                "employees": employees,
                "job_count": job_count,
                "hiring_index": hiring_index
            })

        except Exception as e:

            print(
                f"Error for {company}: {e}"
            )

    return pd.DataFrame(results)


# =========================
# Main
# =========================

def main():

    companies_df = load_companies(
        "VW_Test.xlsx"
    )

    result_df = process_companies(
        companies_df
    )

    save_hiring_index(
        result_df,
        "hiring_index.csv"
    )


if __name__ == "__main__":
    main()