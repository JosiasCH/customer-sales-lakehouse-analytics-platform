from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

CHANNELS = ["Organic Search", "Paid Search", "Email", "Social", "Referral", "Direct"]
REGIONS = ["North America", "Europe", "Latin America", "Asia Pacific"]
CATEGORIES = ["Electronics", "Home", "Beauty", "Sports", "Books", "Fashion"]
ORDER_STATUSES = ["Completed", "Completed", "Completed", "Cancelled", "Returned"]

def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days), seconds=random.randint(0, 86400))

def save(df: pd.DataFrame, name: str) -> None:
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"Saved {len(df):,} rows -> {path}")

def generate_customers(n: int = 1000) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        signup = random_date(datetime(2023, 1, 1), datetime(2025, 12, 31))
        rows.append({
            "customer_id": f"CUST-{i:05d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": f"customer_{i:05d}@example.com",
            "region": random.choice(REGIONS),
            "acquisition_channel": random.choice(CHANNELS),
            "signup_date": signup.date().isoformat(),
            "birth_year": random.randint(1960, 2006),
            "loyalty_tier": random.choices(["Bronze", "Silver", "Gold", "Platinum"], [55, 25, 15, 5])[0],
            "is_active": random.choices([1, 0], [86, 14])[0],
        })
    return pd.DataFrame(rows)

def generate_products(n: int = 300) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        category = random.choice(CATEGORIES)
        price = round(random.uniform(8, 450), 2)
        rows.append({
            "product_id": f"PROD-{i:05d}",
            "product_name": f"{category} Product {i}",
            "category": category,
            "brand": fake.company().replace(",", ""),
            "unit_cost": round(price * random.uniform(0.35, 0.72), 2),
            "list_price": price,
            "is_active": random.choices([1, 0], [92, 8])[0],
        })
    return pd.DataFrame(rows)

def generate_campaigns(n: int = 30) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        start = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 680))
        end = start + timedelta(days=random.randint(7, 60))
        channel = random.choice(CHANNELS)
        rows.append({
            "campaign_id": f"CAMP-{i:04d}",
            "campaign_name": f"{channel} Campaign {i}",
            "channel": channel,
            "start_date": start.date().isoformat(),
            "end_date": end.date().isoformat(),
            "budget": round(random.uniform(1500, 25000), 2),
            "target_region": random.choice(REGIONS),
        })
    return pd.DataFrame(rows)

def generate_orders(customers: pd.DataFrame, campaigns: pd.DataFrame, n: int = 3500) -> pd.DataFrame:
    rows = []
    customer_ids = customers["customer_id"].tolist()
    campaign_ids = campaigns["campaign_id"].tolist()
    for i in range(1, n + 1):
        order_date = random_date(datetime(2024, 1, 1), datetime(2025, 12, 31))
        rows.append({
            "order_id": f"ORD-{i:07d}",
            "customer_id": random.choice(customer_ids),
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "order_status": random.choice(ORDER_STATUSES),
            "sales_channel": random.choice(CHANNELS),
            "campaign_id": random.choice(campaign_ids + [None, None, None]),
            "payment_method": random.choice(["Credit Card", "PayPal", "Apple Pay", "Bank Transfer"]),
            "shipping_region": random.choice(REGIONS),
        })
    return pd.DataFrame(rows)

def generate_order_items(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    rows = []
    product_map = products.set_index("product_id").to_dict(orient="index")
    product_ids = products["product_id"].tolist()
    item_id = 1
    for _, order in orders.iterrows():
        n_items = random.choices([1, 2, 3, 4, 5], [48, 28, 14, 7, 3])[0]
        for product_id in random.sample(product_ids, n_items):
            product = product_map[product_id]
            quantity = random.choices([1, 2, 3, 4], [70, 20, 7, 3])[0]
            discount_rate = random.choices([0, 0.05, 0.10, 0.15, 0.20], [62, 14, 12, 8, 4])[0]
            gross = round(quantity * product["list_price"], 2)
            discount = round(gross * discount_rate, 2)
            rows.append({
                "order_item_id": f"ITEM-{item_id:08d}",
                "order_id": order["order_id"],
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": product["list_price"],
                "discount_rate": discount_rate,
                "gross_amount": gross,
                "discount_amount": discount,
                "net_amount": round(gross - discount, 2),
            })
            item_id += 1
    return pd.DataFrame(rows)

def generate_web_sessions(customers: pd.DataFrame, n: int = 10000) -> pd.DataFrame:
    rows = []
    customer_ids = customers["customer_id"].tolist()
    for i in range(1, n + 1):
        started = random_date(datetime(2024, 1, 1), datetime(2025, 12, 31))
        rows.append({
            "session_id": f"SESS-{i:08d}",
            "customer_id": random.choice(customer_ids + [None, None]),
            "session_start": started.strftime("%Y-%m-%d %H:%M:%S"),
            "channel": random.choice(CHANNELS),
            "device_type": random.choice(["Mobile", "Desktop", "Tablet"]),
            "pages_viewed": random.randint(1, 18),
            "session_duration_seconds": random.randint(20, 3600),
            "converted": random.choices([1, 0], [12, 88])[0],
        })
    return pd.DataFrame(rows)

def generate_email_events(customers: pd.DataFrame, campaigns: pd.DataFrame, n: int = 7000) -> pd.DataFrame:
    rows = []
    customer_ids = customers["customer_id"].tolist()
    campaign_ids = campaigns["campaign_id"].tolist()
    for i in range(1, n + 1):
        sent = random_date(datetime(2024, 1, 1), datetime(2025, 12, 31))
        opened = random.choices([1, 0], [43, 57])[0]
        clicked = random.choices([1, 0], [18 if opened else 3, 82 if opened else 97])[0]
        rows.append({
            "email_event_id": f"EMAIL-{i:08d}",
            "customer_id": random.choice(customer_ids),
            "campaign_id": random.choice(campaign_ids),
            "sent_at": sent.strftime("%Y-%m-%d %H:%M:%S"),
            "opened": opened,
            "clicked": clicked,
            "unsubscribed": random.choices([1, 0], [2, 98])[0],
        })
    return pd.DataFrame(rows)

def generate_support_tickets(customers: pd.DataFrame, orders: pd.DataFrame, n: int = 1200) -> pd.DataFrame:
    rows = []
    customer_ids = customers["customer_id"].tolist()
    order_ids = orders["order_id"].tolist()
    for i in range(1, n + 1):
        created = random_date(datetime(2024, 1, 1), datetime(2025, 12, 31))
        status = random.choices(["Resolved", "Open", "Escalated"], [82, 12, 6])[0]
        resolved = created + timedelta(hours=random.randint(1, 240))
        rows.append({
            "ticket_id": f"TICK-{i:07d}",
            "customer_id": random.choice(customer_ids),
            "order_id": random.choice(order_ids + [None, None, None]),
            "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": resolved.strftime("%Y-%m-%d %H:%M:%S") if status == "Resolved" else None,
            "ticket_category": random.choice(["Delivery", "Payment", "Product Quality", "Refund", "Account", "Other"]),
            "ticket_status": status,
            "priority": random.choice(["Low", "Medium", "High"]),
            "satisfaction_score": random.choice([1, 2, 3, 4, 5, None]),
        })
    return pd.DataFrame(rows)

def main() -> None:
    customers = generate_customers()
    products = generate_products()
    campaigns = generate_campaigns()
    orders = generate_orders(customers, campaigns)
    order_items = generate_order_items(orders, products)
    web_sessions = generate_web_sessions(customers)
    email_events = generate_email_events(customers, campaigns)
    support_tickets = generate_support_tickets(customers, orders)

    save(customers, "customers")
    save(products, "products")
    save(campaigns, "marketing_campaigns")
    save(orders, "orders")
    save(order_items, "order_items")
    save(web_sessions, "web_sessions")
    save(email_events, "email_events")
    save(support_tickets, "support_tickets")

if __name__ == "__main__":
    main()
