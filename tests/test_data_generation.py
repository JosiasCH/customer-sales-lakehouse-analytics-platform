from pathlib import Path
import subprocess
import sys

def test_synthetic_data_generation_creates_expected_files():
    subprocess.run([sys.executable, "scripts/generate_synthetic_retail_data.py"], check=True)
    expected = [
        "customers.csv", "products.csv", "marketing_campaigns.csv", "orders.csv",
        "order_items.csv", "web_sessions.csv", "email_events.csv", "support_tickets.csv"
    ]
    for filename in expected:
        assert (Path("data/raw") / filename).exists()
