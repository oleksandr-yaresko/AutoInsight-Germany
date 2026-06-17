import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

BASE_URL = "https://www.kleinanzeigen.de"
SEARCH_URL = "https://www.kleinanzeigen.de/s-autos/mainz/c216l5315r50"

headers = {
"User-Agent": "Mozilla/5.0"
}

response = requests.get(SEARCH_URL, headers=headers)

print(f"Status code: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

links = []

for a in soup.find_all("a", href=True):
    href = a["href"]

    if "/s-anzeige/" in href:
        full_url = urljoin(BASE_URL, href)

        if full_url not in links:
            links.append(full_url)

print(f"Found {len(links)} listings")

df = pd.DataFrame({"url": links})

df.to_csv(
"data/raw/listing_urls.csv",
index=False,
encoding="utf-8-sig"
)

print("Saved listing_urls.csv")
