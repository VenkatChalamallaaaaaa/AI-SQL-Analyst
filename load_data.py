import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

engine = create_engine("postgresql+psycopg://postgres:admin@localhost:5432/olist")

for csv in Path("data").glob("*.csv"):
    name = csv.stem.replace("olist_", "").replace("_dataset", "")
    df = pd.read_csv(csv)
    for col in df.columns:
        if "timestamp" in col or col.endswith(("_date", "_at")):
            df[col] = pd.to_datetime(df[col])
    df.to_sql(name, engine, if_exists="replace", index=False)
    print(name, len(df))