import pandas as pd

# ==================================
# LOAD DATA
# ==================================

df = pd.read_csv(
    "data/processed/car_listings_clean.csv"
)

print("Cars loaded:", len(df))

# ==================================
# MARKET PRICE
# ==================================

market_price = (
    df.groupby(
        ["brand", "model"]
    )
    .agg(
        ads_count=("price", "count"),
        market_price=("price", "median")
    )
    .reset_index()
)

# Оставляем модели с минимум 5 объявлениями

market_price = market_price[
    market_price["ads_count"] >= 5
]

print(
    "Market models:",
    len(market_price)
)

# ==================================
# MERGE
# ==================================

df = df.merge(
    market_price,
    on=["brand", "model"],
    how="left"
)

# ==================================
# DISCOUNT %
# ==================================

df["discount_percent"] = (
    (
        df["market_price"]
        - df["price"]
    )
    / df["market_price"]
) * 100

df["discount_percent"] = (
    df["discount_percent"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)
# ==================================
# AUTOINSIGHT SCORE
# ==================================

max_mileage = df["mileage"].max()
max_age = df["vehicle_age"].max()

df["discount_score"] = (
    df["discount_percent"]
    .clip(lower=0)
    * 2
).clip(upper=40)

df["mileage_score"] = (
    25 * (1 - df["mileage"] / max_mileage)
).clip(lower=0)

df["age_score"] = (
    20 * (1 - df["vehicle_age"] / max_age)
).clip(lower=0)

df["popularity_score"] = (
    df["ads_count"]
    .clip(upper=15)
)

df["autoinsight_score"] = (
    df["discount_score"]
    + df["mileage_score"]
    + df["age_score"]
    + df["popularity_score"]
)

df["autoinsight_score"] = (
    df["autoinsight_score"]
    .fillna(0)
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .clip(0, 100)
    .round()
    .astype(int)
)

# ==================================
# CLASSIFICATION
# ==================================

def classify(score):

    if score >= 90:
        return "Exceptional Deal"

    elif score >= 70:
        return "Good Deal"

    elif score >= 40:
        return "Fair Value"

    return "Overpriced"


df["classification"] = (
    df["autoinsight_score"]
    .apply(classify)
)

# ==================================
# TOP DEALS
# ==================================

top_deals = (
    df
    .sort_values(
        "autoinsight_score",
        ascending=False
    )
    .head(20)
)

print("\nTOP 20 HIDDEN DEALS\n")

print(
    top_deals[
        [
            "brand",
            "model",
            "price",
            "market_price",
            "discount_percent",
            "autoinsight_score",
            "classification"
        ]
    ]
)

# ==================================
# REMOVE NULL MARKET PRICE
# ==================================

df = df[
    df["market_price"].notna()
]

print(
    "Cars with market price:",
    len(df)
)

# ==================================
# SAVE
# ==================================

df.to_csv(
    "data/processed/car_deals.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nSaved:")
print("data/processed/car_deals.csv")