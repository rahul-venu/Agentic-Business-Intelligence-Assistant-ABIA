import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

np.random.seed(13)

# -----------------------
# CONFIG & REGIONAL MAP
# -----------------------
NUM_CUSTOMERS = 500
NUM_PRODUCTS = 100
NUM_ORDERS = 5000

# 1. Define a logical mapping between Country and Region
COUNTRY_REGION_MAP = {
    "USA": "North America",
    "UK": "Europe",
    "Germany": "Europe",
    "India": "Asia",
}

countries = list(COUNTRY_REGION_MAP.keys())
channels = ["Web", "Mobile"]
categories = ["Electronics", "Clothing", "Home", "Sports"]

# -----------------------
# CUSTOMER DATA
# -----------------------
customer_ids = [f"CUST_{i}" for i in range(1, NUM_CUSTOMERS + 1)]

# Create customers with a mapped region
customer_countries = np.random.choice(countries, NUM_CUSTOMERS)

customer_data = pd.DataFrame(
    {
        "customer_id": customer_ids,
        "signup_date": [
            datetime(2022, 1, 1) + timedelta(days=random.randint(0, 900))
            for _ in range(NUM_CUSTOMERS)
        ],
        "segment": np.random.choice(["Basic", "Premium"], NUM_CUSTOMERS, p=[0.7, 0.3]),
        "country": customer_countries,
    }
)

customer_data["churned"] = np.where(
    (customer_data["segment"] == "Basic") & (np.random.rand(NUM_CUSTOMERS) > 0.7),
    True,
    False,
)

# -----------------------
# PRODUCT DATA
# -----------------------
product_ids = [f"PROD_{i}" for i in range(1, NUM_PRODUCTS + 1)]

product_data = pd.DataFrame(
    {
        "product_id": product_ids,
        "category": np.random.choice(categories, NUM_PRODUCTS),
        "price": np.round(np.random.uniform(10, 500, NUM_PRODUCTS), 2),
    }
)

product_data["cost"] = product_data["price"] * np.random.uniform(0.4, 0.8, NUM_PRODUCTS)

# -----------------------
# SALES DATA
# -----------------------
# Create a fast lookup dict for customer -> country/region
cust_country_lookup = dict(zip(customer_data["customer_id"], customer_data["country"]))


def random_date():
    return datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))


sales_records = []

for i in range(NUM_ORDERS):
    cust = random.choice(customer_ids)
    prod = random.choice(product_ids)

    price = product_data.loc[product_data["product_id"] == prod, "price"].values[0]
    quantity = np.random.randint(1, 5)
    revenue = price * quantity

    # 2. Derive region directly from the customer's country!
    cust_country = cust_country_lookup[cust]
    region = COUNTRY_REGION_MAP[cust_country]

    # Inject anomaly for Europe
    if region == "Europe" and random.random() < 0.2:
        revenue *= 0.6  # simulate problem

    sales_records.append(
        {
            "order_id": f"ORD_{i}",
            "date": random_date(),
            "customer_id": cust,
            "product_id": prod,
            "revenue": round(revenue, 2),
            "quantity": quantity,
            "region": region,
            "channel": random.choice(channels),
        }
    )

sales_data = pd.DataFrame(sales_records)

# -----------------------
# SAVE FILES
# -----------------------
customer_data.to_csv("data/customer_data.csv", index=False)
product_data.to_csv("data/product_data.csv", index=False)
sales_data.to_csv("data/sales_data.csv", index=False)

print("Synthetic data generated successfully inside data/!")
