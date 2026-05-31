from src.utils.paths import RAW_DIR, BRONZE_DIR, TABLES
from src.utils.spark import get_spark

def build_bronze() -> None:
    spark = get_spark("build-bronze")
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    for table in TABLES:
        source = RAW_DIR / f"{table}.csv"
        target = BRONZE_DIR / table
        if not source.exists():
            raise FileNotFoundError(f"Missing raw file: {source}")
        df = spark.read.option("header", True).option("inferSchema", True).csv(str(source))
        df.write.mode("overwrite").parquet(str(target))
        print(f"Bronze table written: {table} -> {target}")
    spark.stop()

if __name__ == "__main__":
    build_bronze()
