import os
import requests
from tqdm import tqdm
from zipfile import ZipFile

BASE_URL = "https://hmmt-archive.s3.amazonaws.com/tournaments"
YEARS = list(range(2008, 2026))
MONTHS = ["feb", "nov"]

SKIP = set()

LOG_MISSING = "hmmt_missing_files.log"

def get_categories(year, month):
    if month == "nov":
        if year <= 2010:
            return ["gen1", "gen2", "guts", "team"]
        elif 2011 <= year <= 2024:
            return ["gen", "thm", "guts", "team"]
    elif month == "feb":
        if year <= 2010:
            return ["alg", "calc", "comb", "geo", "gen1", "gen2", "guts", "team1", "team2"]
        elif year == 2011:
            return ["algcalc", "algcomb", "alggeo", "calccomb", "calcgeo", "combgeo", "guts", "team1", "team2"]
        elif year == 2012:
            return ["alg", "comb", "geo", "guts", "team1", "team2"]
        elif 2013 <= year <= 2016:
            return ["alg", "comb", "geo", "guts", "team"]
        elif 2017 <= year <= 2025:
            return ["algnt", "comb", "geo", "guts", "team"]
    return []

def file_exists(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except requests.RequestException:
        return False

def download_file(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        r = requests.get(url, timeout=10)
        with open(path, "wb") as f:
            f.write(r.content)
    except requests.RequestException:
        print(f"  ❌ Failed to download: {url}")
        return False
    return True

def main():
    downloads = []
    missing = []

    for year in YEARS:
        for month in MONTHS:
            categories = get_categories(year, month)
            for cat in categories:
                for doc_type in ["problems", "solutions"]:
                    url = f"{BASE_URL}/{year}/{month}/{cat}/{doc_type}.pdf"
                    local_path = f"HMMT/{year}/{month}/{doc_type.capitalize()}/{cat}.pdf"

                    if file_exists(url):
                        downloads.append((url, local_path))
                        print(f"✅ Found: {url}")
                    else:
                        print(f"❌ Missing: {url}")
                        missing.append(url)

    print("\n📥 Downloading available files...\n")
    for url, path in tqdm(downloads, desc="Downloading"):
        print(f"⬇️  Downloading: {url} → {path}")
        download_file(url, path)

    print("\n📦 Zipping into HMMT.zip...")
    with ZipFile("HMMT.zip", "w") as z:
        for root, _, files in os.walk("HMMT"):
            for file in files:
                full = os.path.join(root, file)
                arcname = os.path.relpath(full, "HMMT")
                z.write(full, os.path.join("HMMT", arcname))

    if missing:
        with open(LOG_MISSING, "w") as log:
            for m in missing:
                log.write(m + "\n")
        print(f"\n📝 Missing files logged to {LOG_MISSING}")
    else:
        print("\n✅ All available files found and downloaded.")

    print("\n🎉 Done! Archive saved as HMMT.zip")

if __name__ == "__main__":
    main()
