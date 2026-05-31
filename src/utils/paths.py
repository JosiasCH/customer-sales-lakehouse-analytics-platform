from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

TABLES = [
    "customers",
    "products",
    "marketing_campaigns",
    "orders",
    "order_items",
    "web_sessions",
    "email_events",
    "support_tickets",
]
