import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time

# =====================================================
# НАСТРОЙКИ
# =====================================================

BASE_URL = "https://www.kleinanzeigen.de"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Сколько страниц собираем
MAX_PAGES = 50

all_links = []

# =====================================================
# ЦИКЛ ПО СТРАНИЦАМ
# =====================================================

for page in range(1, MAX_PAGES + 1):

    # Первая страница без параметра seite
    if page == 1:
        search_url = (
            f"https://www.kleinanzeigen.de/s-autos/mainz/"
            f"seite:{page}/c216l5315r50"
        )

    else:
        search_url = (
            f"https://www.kleinanzeigen.de/s-autos/mainz/"
            f"seite:{page}/c216l5315r50"
        )

    print(f"\nСтраница {page}")
    print(search_url)

    try:

        response = requests.get(
            search_url,
            headers=HEADERS,
            timeout=20
        )

        print("Status:", response.status_code)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        page_links = []

        for a in soup.find_all("a", href=True):

            href = a["href"]

                           

            # Только объявления
            if not href.startswith("/s-anzeige/"):
                continue

            full_url = urljoin(
                BASE_URL,
                href
            )

            if full_url not in page_links:
                page_links.append(full_url)

                full_url = urljoin(
                    BASE_URL,
                    href
                )

                if full_url not in page_links:
                    page_links.append(full_url)

        print(
            f"Найдено объявлений: {len(page_links)}"
        )

        all_links.extend(page_links)

        # Пауза между запросами
        time.sleep(2)

    except Exception as e:

        print("Ошибка:", e)

# =====================================================
# УДАЛЯЕМ ДУБЛИКАТЫ
# =====================================================

all_links = list(set(all_links))

print("\nИТОГО:")
print("Уникальных объявлений:", len(all_links))

# =====================================================
# СОХРАНЯЕМ CSV
# =====================================================

df = pd.DataFrame({
    "url": all_links
})

df.to_csv(
    "data/raw/listing_urls.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nФайл сохранён")