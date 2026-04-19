import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from datetime import datetime
from dotenv import load_dotenv
import os

# ── Connect to PostgreSQL ──────────────────────────────────────────

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

# ── Load Data ──────────────────────────────────────────────────────
print("Loading data...")
orders = pd.read_sql("SELECT * FROM orders", engine)
payments = pd.read_sql("SELECT * FROM order_payments", engine)
customers = pd.read_sql("SELECT * FROM customers", engine)

# ── Prepare Data ───────────────────────────────────────────────────
# Convert date column
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])

# Only delivered orders
orders = orders[orders['order_status'] == 'delivered']

# ── RFM Calculation ────────────────────────────────────────────────
snapshot_date = orders['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

# Merge orders with payments
order_payments = orders.merge(payments, on='order_id')

rfm = order_payments.groupby('customer_id').agg(
    Recency=('order_purchase_timestamp', lambda x: (snapshot_date - x.max()).days),
    Frequency=('order_id', 'nunique'),
    Monetary=('payment_value', 'sum')
).reset_index()

print("\n📊 RFM Summary:")
print(rfm.describe().round(2))

# ── RFM Scoring ────────────────────────────────────────────────────
rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])

rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

# ── Customer Segments ──────────────────────────────────────────────
def segment(row):
    r = int(row['R_Score'])
    f = int(row['F_Score'])
    m = int(row['M_Score'])
    if r >= 3 and f >= 3:
        return 'Champions'
    elif r >= 3 and f >= 2:
        return 'Loyal Customers'
    elif r >= 3:
        return 'Recent Customers'
    elif r == 2 and f >= 2:
        return 'At Risk'
    else:
        return 'Lost Customers'

rfm['Segment'] = rfm.apply(segment, axis=1)

print("\n👥 Customer Segments:")
print(rfm['Segment'].value_counts())

# ── Save Results ───────────────────────────────────────────────────
output_path = "F:/BA Projects/Retail Portfolio/01_customer_analysis/python/"
rfm.to_csv(output_path + "rfm_results.csv", index=False)
print("\n✅ RFM results saved to rfm_results.csv")

# ── Visualizations ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Customer RFM Analysis - Olist E-commerce', fontsize=16)

# Recency
axes[0].hist(rfm['Recency'], bins=30, color='steelblue', edgecolor='white')
axes[0].set_title('Recency Distribution')
axes[0].set_xlabel('Days Since Last Purchase')
axes[0].set_ylabel('Number of Customers')

# Frequency
axes[1].hist(rfm['Frequency'], bins=20, color='seagreen', edgecolor='white')
axes[1].set_title('Frequency Distribution')
axes[1].set_xlabel('Number of Orders')
axes[1].set_ylabel('Number of Customers')

# Monetary
axes[2].hist(rfm['Monetary'], bins=30, color='coral', edgecolor='white')
axes[2].set_title('Monetary Distribution')
axes[2].set_xlabel('Total Spend (R$)')
axes[2].set_ylabel('Number of Customers')

plt.tight_layout()
plt.savefig(output_path + "rfm_distributions.png", dpi=150)
plt.show()
print("✅ Charts saved!")
