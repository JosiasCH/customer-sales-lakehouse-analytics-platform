from pyspark.sql import functions as F
from src.utils.paths import BRONZE_DIR, SILVER_DIR, TABLES
from src.utils.spark import get_spark

def read_bronze(spark, table):
    return spark.read.parquet(str(BRONZE_DIR / table))

def write_silver(df, table):
    target = SILVER_DIR / table
    df.write.mode("overwrite").parquet(str(target))
    print(f"Silver table written: {table} -> {target}")

def build_silver() -> None:
    spark = get_spark("build-silver")
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    customers = read_bronze(spark, "customers").dropDuplicates(["customer_id"])         .withColumn("signup_date", F.to_date("signup_date"))         .withColumn("birth_year", F.col("birth_year").cast("int"))         .withColumn("is_active", F.col("is_active").cast("int"))

    products = read_bronze(spark, "products").dropDuplicates(["product_id"])         .withColumn("unit_cost", F.col("unit_cost").cast("double"))         .withColumn("list_price", F.col("list_price").cast("double"))         .withColumn("is_active", F.col("is_active").cast("int"))

    campaigns = read_bronze(spark, "marketing_campaigns").dropDuplicates(["campaign_id"])         .withColumn("start_date", F.to_date("start_date"))         .withColumn("end_date", F.to_date("end_date"))         .withColumn("budget", F.col("budget").cast("double"))

    orders = read_bronze(spark, "orders").dropDuplicates(["order_id"])         .withColumn("order_date", F.to_timestamp("order_date"))

    order_items = read_bronze(spark, "order_items").dropDuplicates(["order_item_id"])         .withColumn("quantity", F.col("quantity").cast("int"))         .withColumn("unit_price", F.col("unit_price").cast("double"))         .withColumn("discount_rate", F.col("discount_rate").cast("double"))         .withColumn("gross_amount", F.col("gross_amount").cast("double"))         .withColumn("discount_amount", F.col("discount_amount").cast("double"))         .withColumn("net_amount", F.col("net_amount").cast("double"))

    web_sessions = read_bronze(spark, "web_sessions").dropDuplicates(["session_id"])         .withColumn("session_start", F.to_timestamp("session_start"))         .withColumn("pages_viewed", F.col("pages_viewed").cast("int"))         .withColumn("session_duration_seconds", F.col("session_duration_seconds").cast("int"))         .withColumn("converted", F.col("converted").cast("int"))

    email_events = read_bronze(spark, "email_events").dropDuplicates(["email_event_id"])         .withColumn("sent_at", F.to_timestamp("sent_at"))         .withColumn("opened", F.col("opened").cast("int"))         .withColumn("clicked", F.col("clicked").cast("int"))         .withColumn("unsubscribed", F.col("unsubscribed").cast("int"))

    support_tickets = read_bronze(spark, "support_tickets").dropDuplicates(["ticket_id"])         .withColumn("created_at", F.to_timestamp("created_at"))         .withColumn("resolved_at", F.to_timestamp("resolved_at"))         .withColumn("satisfaction_score", F.col("satisfaction_score").cast("int"))

    for name, df in [
        ("customers", customers), ("products", products), ("marketing_campaigns", campaigns),
        ("orders", orders), ("order_items", order_items), ("web_sessions", web_sessions),
        ("email_events", email_events), ("support_tickets", support_tickets)
    ]:
        write_silver(df, name)

    spark.stop()

if __name__ == "__main__":
    build_silver()
