import pandas as pd
from sqlalchemy import create_engine

# ==========================================
# Загружаем очищенный датасет
# ==========================================

df = pd.read_csv(
    "data/processed/car_listings_clean.csv"
)

# ==========================================
# Подключение к PostgreSQL
# ==========================================

engine = create_engine(
    "postgresql+psycopg2://postgres:190882@localhost:5432/autoinsight_germany"
)

# ==========================================
# Загружаем данные в таблицу
# ==========================================

df.to_sql(
    "vehicle_listings",
    engine,
    if_exists="append",
    index=False
)

print("Data loaded successfully")
print("Rows loaded:", len(df))