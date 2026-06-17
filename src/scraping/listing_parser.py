import requests
import pandas as pd
import re
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

df_urls = pd.read_csv("data/raw/listing_urls.csv")

urls = df_urls["url"].tolist()

cars = []


def parse_attributes(attr_string):

    result = {}

    for pair in attr_string.split("|"):

        if ":" in pair:
            key, value = pair.split(":", 1)
            result[key] = value

    return result


for i, url in enumerate(urls, start=1):

    print(f"[{i}/{len(urls)}] {url}")

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        html = response.text

        price_match = re.search(
            r'"ad_price":"([\d\.]+)"',
            html
        )

        seller_match = re.search(
            r'"ad_seller_type":"([^"]+)"',
            html
        )

        attr_match = re.search(
            r'"ad_attributes":"([^"]+)"',
            html
        )

        if not attr_match:
            continue

        attrs = parse_attributes(
            attr_match.group(1)
        )

        car = {

            "brand": attrs.get("marke_s"),
            "model": attrs.get("model_s"),

            "price": price_match.group(1)
            if price_match else None,

            "year": attrs.get("ez_i"),
            "month": attrs.get("ezm_i"),

            "mileage": attrs.get("km_i"),

            "fuel_type": attrs.get("fuel_s"),

            "transmission": attrs.get("shift_s"),

            "power_hp": attrs.get("power_i"),

            "vehicle_type": attrs.get("typ_s"),

            "seller_type": seller_match.group(1)
            if seller_match else None,

            "damage": attrs.get("schaden_s"),

            "url": url,

            "scrape_date": datetime.now()
        }

        cars.append(car)

    except Exception as e:

        print("ERROR:", e)


df = pd.DataFrame(cars)

df.to_csv(
    "data/raw/car_listings.csv",
    index=False,
    encoding="utf-8-sig"
)

print()
print("Records saved:", len(df))
print(df.head())