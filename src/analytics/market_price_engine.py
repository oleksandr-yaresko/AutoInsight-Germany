import pandas as pd

# ==================================
# LOAD DATA
# ==================================

df = pd.read_csv(
    "data/processed/car_listings_clean.csv"
)

initial_cars = len(df)

print("Cars loaded:", initial_cars)

# ==================================
# AGE GROUP
# ==================================

df["age_group"] = pd.cut(
    df["vehicle_age"],
    bins=[0, 5, 10, 15, 100],
    labels=[
        "0-5",
        "6-10",
        "11-15",
        "15+"
    ]
)

# ==================================
# MILEAGE GROUP
# ==================================

#df["mileage_group"] = pd.cut(
#   df["mileage"],
#    bins=[
#        0,
#        50000,
#        100000,
#        150000,
#        200000,
#        1000000
#    ],
#    labels=[
#        "0-50k",
#        "50-100k",
#        "100-150k",
#        "150-200k",
#        "200k+"
#    ]
#)

# ==================================
# MARKET PRICE
# ==================================

market_price = (
    df.groupby(
        [
            "brand",
            "model",
            "age_group"            
        ]
    )
    .agg(
        ads_count=("price", "count"),
        market_price=("price", "median")
    )
    .reset_index()
)

market_price = market_price[
    market_price["ads_count"] >= 3
]

print(
    "Market segments:",
    len(market_price)
)

market_price["liquidity_score"] = (
    market_price["ads_count"]
    / market_price["ads_count"].max()
) * 15

# ==================================
# MERGE
# ==================================

df = df.merge(
    market_price,
    on=[
        "brand",
        "model",
        "age_group"        
    ],
    how="left"
)

df["liquidity_score"] = (
    df["liquidity_score"]
    .fillna(0)
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


df["autoinsight_score"] = (
    df["discount_score"]
    + df["mileage_score"]
    + df["age_score"]
    + df["liquidity_score"]
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
# REASONS ENGINE
# ==================================

def build_reasons(row):

    reasons = []

    if row["discount_percent"] >= 20:
        reasons.append("20%+ below market value")

    elif row["discount_percent"] >= 10:
        reasons.append("Below market value")

    if row["vehicle_age"] <= 5:
        reasons.append("Modern vehicle")

    if row["mileage"] <= 100000:
        reasons.append("Low mileage")

    if row["ads_count"] >= 10:
        reasons.append("Popular model")

    return " | ".join(reasons)


df["reasons"] = df.apply(
    build_reasons,
    axis=1
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
# FAIR PRICE
# ==================================

df["fair_price"] = (
    df["market_price"]
    .round(0)
    .astype("Int64")
)

# ==================================
# TOP DEALS
# ==================================

top_deals = df[
    (df["price"] >= 3000)
    & (df["vehicle_age"] <= 15)
    & (df["mileage"] <= 250000)
]

top_deals = (
    top_deals
    .sort_values(
        "autoinsight_score",
        ascending=False
    )
    .drop_duplicates(
        subset=["brand", "model"]
    )
    .head(20)
)

top_deals.insert(
    0,
    "rank",
    range(1, len(top_deals) + 1)
)

print("\nTOP 20 HIDDEN DEALS\n")

for i, (_, row) in enumerate(
    top_deals.iterrows(),
    start=1
):

    print(
        f"""
#{i}

{row['brand']} {row['model']}

Price: €{row['price']:,.0f}
Fair Price: €{row['fair_price']:,.0f}

AutoInsight Score: {row['autoinsight_score']}

Classification:
{row['classification']}

Reasons:
{row['reasons']}
"""
    )

# ==================================
# SAVE FILES
# ==================================

df["savings_eur"] = (
    df["fair_price"] - df["price"]
)

df["savings_percent"] = (
    (df["fair_price"] - df["price"])
    / df["fair_price"]
) * 100

df.to_csv(
    "data/processed/car_deals.csv",
    index=False,
    encoding="utf-8-sig"
)

top_deals.to_csv(
    "data/processed/top_hidden_deals.csv",
    index=False,
    encoding="utf-8-sig"
)



print("\nSUMMARY")
print("-" * 30)

print("Initial Cars:", initial_cars)
print("Cars With Fair Price:", len(df))
print("Market Segments:", len(market_price))
print("Top Deals:", len(top_deals))

print(
    "Average Score:",
    round(df["autoinsight_score"].mean(), 1)
)