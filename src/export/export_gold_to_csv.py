from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

GOLD_DIR = PROJECT_ROOT / "data" / "gold"
POWERBI_DIR = PROJECT_ROOT / "data" / "powerbi"

GOLD_TABLES = [
    "dim_customer",
    "dim_product",
    "dim_campaign",
    "fact_orders",
    "fact_web_sessions",
    "fact_email_events",
    "fact_support_tickets",
    "customer_analytics",
    "marketing_performance",
]


def ensure_output_dir() -> None:
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)


def read_gold_table(table_name: str) -> pd.DataFrame:
    table_path = GOLD_DIR / table_name

    if not table_path.exists():
        raise FileNotFoundError(
            f"Gold table not found: {table_path}. "
            "Run `python -m src.gold.build_gold` before exporting to Power BI."
        )

    return pd.read_parquet(table_path)


def export_table_to_csv(table_name: str) -> dict:
    df = read_gold_table(table_name)

    output_path = POWERBI_DIR / f"{table_name}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    result = {
        "table_name": table_name,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "output_file": str(output_path.relative_to(PROJECT_ROOT)),
    }

    print(
        f"Exported {table_name}: "
        f"{result['rows']:,} rows, {result['columns']} columns -> {output_path}"
    )

    return result


def copy_quality_summary() -> dict | None:
    source_path = GOLD_DIR / "pipeline_quality_summary.csv"
    target_path = POWERBI_DIR / "pipeline_quality_summary.csv"

    if not source_path.exists():
        print("Quality summary not found. Skipping pipeline_quality_summary.csv export.")
        return None

    shutil.copy2(source_path, target_path)

    df = pd.read_csv(target_path)

    result = {
        "table_name": "pipeline_quality_summary",
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "output_file": str(target_path.relative_to(PROJECT_ROOT)),
    }

    print(
        f"Copied pipeline_quality_summary: "
        f"{result['rows']:,} rows, {result['columns']} columns -> {target_path}"
    )

    return result


def write_export_manifest(results: list[dict]) -> None:
    manifest = {
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_layer": "data/gold",
        "target_layer": "data/powerbi",
        "tables": results,
    }

    output_path = POWERBI_DIR / "powerbi_export_manifest.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)

    print(f"Export manifest written -> {output_path}")


def main() -> None:
    ensure_output_dir()

    results = []

    for table_name in GOLD_TABLES:
        results.append(export_table_to_csv(table_name))

    quality_result = copy_quality_summary()
    if quality_result is not None:
        results.append(quality_result)

    write_export_manifest(results)

    print("\nPower BI export layer completed successfully.")


if __name__ == "__main__":
    main()