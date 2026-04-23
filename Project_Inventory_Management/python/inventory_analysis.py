import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
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

query = """
SELECT 
    ct.product_category_name_english AS category,
    COUNT(oi.order_id) AS total_orders,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_price,
    ROUND((100.0 * SUM(oi.price) / SUM(SUM(oi.price)) OVER())::numeric, 2) AS revenue_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY ct.product_category_name_english
ORDER BY total_orders DESC
"""

df = pd.read_sql(query, engine)
print(f"✅ Loaded {len(df)} categories")

# ── Inventory Classification ───────────────────────────────────────
avg_orders = df['total_orders'].mean()
avg_revenue = df['total_revenue'].mean()

def classify_inventory(row):
    if row['total_orders'] > avg_orders and row['total_revenue'] > avg_revenue:
        return '🟢 Star Product'
    elif row['total_orders'] > avg_orders and row['total_revenue'] <= avg_revenue:
        return '🟡 High Volume Low Value'
    elif row['total_orders'] <= avg_orders and row['total_revenue'] > avg_revenue:
        return '🔵 High Value Low Volume'
    else:
        return '🔴 Dead Stock'

df['inventory_status'] = df.apply(classify_inventory, axis=1)

print("\n📦 Inventory Status Summary:")
print(df['inventory_status'].value_counts())

print("\n🟢 Star Products:")
print(df[df['inventory_status'] == '🟢 Star Product'][['category', 'total_orders', 'total_revenue']])

print("\n🔴 Dead Stock Categories:")
print(df[df['inventory_status'] == '🔴 Dead Stock'][['category', 'total_orders', 'total_revenue']].head(10))

# ── Save Results ───────────────────────────────────────────────────
output_path = "F:/BA Projects/Retail Portfolio/Project_Inventory_Management/python/"
df.to_csv(output_path + "inventory_analysis.csv", index=False)
print("\n✅ Results saved!")

# ── Visualizations ─────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Inventory Analysis - Olist E-commerce', fontsize=16)

# Top 10 categories by orders
top10 = df.nlargest(10, 'total_orders')
axes[0, 0].barh(top10['category'], top10['total_orders'], color='steelblue')
axes[0, 0].set_title('Top 10 Categories by Orders')
axes[0, 0].set_xlabel('Total Orders')

# Top 10 categories by revenue
top10_rev = df.nlargest(10, 'total_revenue')
axes[0, 1].barh(top10_rev['category'], top10_rev['total_revenue'], color='seagreen')
axes[0, 1].set_title('Top 10 Categories by Revenue')
axes[0, 1].set_xlabel('Total Revenue (R$)')

# Inventory status distribution
status_counts = df['inventory_status'].value_counts()
axes[1, 0].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
axes[1, 0].set_title('Inventory Status Distribution')

# Revenue percentage - top 15
top15 = df.nlargest(15, 'revenue_pct')
axes[1, 1].bar(range(len(top15)), top15['revenue_pct'], color='coral')
axes[1, 1].set_xticks(range(len(top15)))
axes[1, 1].set_xticklabels(top15['category'], rotation=45, ha='right', fontsize=8)
axes[1, 1].set_title('Revenue % by Category (Top 15)')
axes[1, 1].set_ylabel('Revenue %')

plt.tight_layout()
plt.savefig(output_path + "inventory_analysis.png", dpi=150)
plt.show()
print("✅ Charts saved!")