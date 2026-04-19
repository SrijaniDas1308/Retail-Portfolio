import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os

# Connect to PostgreSQL

load_dotenv()

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME")
)

engine = create_engine(connection_url)

# Path to your data folder
data_path = "F:/BA Projects/Retail Portfolio/data/"

# Load all CSV files into PostgreSQL
tables = {
    'customers': 'olist_customers_dataset.csv',
    'orders': 'olist_orders_dataset.csv',
    'order_items': 'olist_order_items_dataset.csv',
    'order_payments': 'olist_order_payments_dataset.csv',
    'order_reviews': 'olist_order_reviews_dataset.csv',
    'products': 'olist_products_dataset.csv',
    'sellers': 'olist_sellers_dataset.csv',
    'geolocation': 'olist_geolocation_dataset.csv',
    'category_translation': 'product_category_name_translation.csv'
}

for table_name, file_name in tables.items():
    df = pd.read_csv(data_path + file_name)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"✅ Loaded {table_name} — {len(df)} rows")

print("\n🎉 All tables loaded into PostgreSQL!")
