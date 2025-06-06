import pandas as pd
from sqlalchemy import create_engine

MYSQL_USER = "Jhered"
MYSQL_PASSWORD = "Jhered143!"
MYSQL_HOST = "localhost"
MYSQL_DB = "hexahaul_db"

CSV_PATH = r"hexahaul_db/hh_user-login.csv"

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
)

df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)

# Remove duplicate emails in the CSV itself
df = df.drop_duplicates(subset=["Email Address"])

# Normalize emails in DataFrame
df["Email Address"] = df["Email Address"].str.strip().str.lower()

# Get existing emails from the database and normalize
with engine.connect() as conn:
    existing_emails = pd.read_sql("SELECT `Email Address` FROM user_login", conn)["Email Address"].str.strip().str.lower().tolist()

# Filter out rows with duplicate emails already in the database
df = df[~df["Email Address"].isin(existing_emails)]

if not df.empty:
    df.to_sql("user_login", con=engine, if_exists="append", index=False)
    print("Import complete!")
else:
    print("No new users to import.")