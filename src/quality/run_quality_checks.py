import pandas as pd
from src.utils.paths import RAW_DIR, BRONZE_DIR, SILVER_DIR, GOLD_DIR, TABLES
from src.utils.spark import get_spark

def parquet_count(spark, path):
    return spark.read.parquet(str(path)).count() if path.exists() else 0

def run_quality_checks():
    spark = get_spark("quality-checks")
    rows = []
    for table in TABLES:
        raw_path = RAW_DIR / f"{table}.csv"
        rows.append({
            "table_name": table,
            "raw_count": pd.read_csv(raw_path).shape[0] if raw_path.exists() else 0,
            "bronze_count": parquet_count(spark, BRONZE_DIR / table),
            "silver_count": parquet_count(spark, SILVER_DIR / table),
        })

    for table in ["dim_customer", "dim_product", "dim_campaign", "fact_orders", "customer_analytics", "marketing_performance"]:
        rows.append({
            "table_name": f"gold.{table}",
            "raw_count": None,
            "bronze_count": None,
            "silver_count": parquet_count(spark, GOLD_DIR / table),
        })

    output = GOLD_DIR / "pipeline_quality_summary.csv"
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"Quality summary written -> {output}")
    spark.stop()

if __name__ == "__main__":
    run_quality_checks()
