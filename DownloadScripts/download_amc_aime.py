import os
import requests
from tqdm import tqdm
from zipfile import ZipFile

AIME_BASE = "https://artofproblemsolving.com/community/contest/download/c3416"
AMC12_BASE = "https://artofproblemsolving.com/community/contest/download/c3415_amc_12"

AIME_YEARS = list(range(1983, 2026))
AMC12_YEARS = list(range(2000, 2026))

def file_exists(url):
    try:
        r = requests.get(url, stream=True, timeout=5, allow_redirects=True)
        return r.status_code == 200 and 'application/pdf' in r.headers.get('Content-Type', '')
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

    # AIME
    for year in AIME_YEARS:
        url = f"{AIME_BASE}/{year}"
        local_path = f"AIME/aime{year}.pdf"
        if file_exists(url):
            downloads.append((url, local_path))
            print(f"✅ Found: {url}")
        else:
            print(f"❌ Missing: {url}")
            missing.append(url)

    # AMC 12
    for year in AMC12_YEARS:
        url = f"{AMC12_BASE}/{year}"
        local_path = f"AMC12/amc{year}.pdf"
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

    print("\n📦 Zipping into Contests.zip...")
    with ZipFile("Contests.zip", "w") as z:
        for root, _, files in os.walk("."):
            for file in files:
                if file.endswith(".pdf"):
                    full = os.path.join(root, file)
                    arcname = os.path.relpath(full, ".")
                    z.write(full, arcname)

    if missing:
        with open("missing_files.log", "w") as log:
            for m in missing:
                log.write(m + "\n")
        print("\n📝 Missing files logged to missing_files.log")
    else:
        print("\n✅ All available files found and downloaded.")

    print("\n🎉 Done! Archive saved as Contests.zip")

if __name__ == "__main__":
    main()