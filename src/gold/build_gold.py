from pyspark.sql import functions as F
from src.utils.paths import SILVER_DIR, GOLD_DIR
from src.utils.spark import get_spark

def read_silver(spark, table):
    return spark.read.parquet(str(SILVER_DIR / table))

def write_gold(df, table):
    target = GOLD_DIR / table
    df.write.mode("overwrite").parquet(str(target))
    print(f"Gold table written: {table} -> {target}")

def build_gold() -> None:
    spark = get_spark("build-gold")
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    customers = read_silver(spark, "customers")
    products = read_silver(spark, "products")
    campaigns = read_silver(spark, "marketing_campaigns")
    orders = read_silver(spark, "orders")
    order_items = read_silver(spark, "order_items")
    web_sessions = read_silver(spark, "web_sessions")
    email_events = read_silver(spark, "email_events")
    support_tickets = read_silver(spark, "support_tickets")

    dim_customer = customers.select("customer_id", "region", "acquisition_channel", "signup_date", "birth_year", "loyalty_tier", "is_active")
    dim_product = products.select("product_id", "product_name", "category", "brand", "unit_cost", "list_price", "is_active")
    dim_campaign = campaigns.select("campaign_id", "campaign_name", "channel", "start_date", "end_date", "budget", "target_region")

    fact_orders = orders.alias("o").join(order_items.alias("oi"), "order_id", "left").join(products.alias("p"), "product_id", "left").select(
        "o.order_id", "oi.order_item_id", "o.customer_id", "oi.product_id", "o.campaign_id",
        "o.order_date", F.to_date("o.order_date").alias("order_day"),
        F.date_format("o.order_date", "yyyy-MM").alias("order_month"),
        "o.order_status", "o.sales_channel", "o.payment_method", "o.shipping_region",
        "oi.quantity", "oi.gross_amount", "oi.discount_amount", "oi.net_amount",
        ((F.col("oi.unit_price") - F.col("p.unit_cost")) * F.col("oi.quantity")).alias("estimated_margin")
    )

    customer_orders = fact_orders.filter(F.col("order_status") == "Completed").groupBy("customer_id").agg(
        F.countDistinct("order_id").alias("completed_orders"),
        F.round(F.sum("net_amount"), 2).alias("total_revenue"),
        F.max("order_day").alias("last_order_date"),
        F.min("order_day").alias("first_order_date")
    )

    sessions = web_sessions.groupBy("customer_id").agg(
        F.countDistinct("session_id").alias("total_sessions"),
        F.sum("converted").alias("converted_sessions"),
        F.round(F.avg("pages_viewed"), 2).alias("avg_pages_viewed")
    )

    emails = email_events.groupBy("customer_id").agg(
        F.count("*").alias("emails_sent"),
        F.sum("opened").alias("emails_opened"),
        F.sum("clicked").alias("emails_clicked")
    )

    tickets = support_tickets.groupBy("customer_id").agg(
        F.count("*").alias("support_tickets"),
        F.sum(F.when(F.col("ticket_status") != "Resolved", 1).otherwise(0)).alias("open_tickets"),
        F.round(F.avg("satisfaction_score"), 2).alias("avg_satisfaction_score")
    )

    customer_analytics = dim_customer.join(customer_orders, "customer_id", "left").join(sessions, "customer_id", "left").join(emails, "customer_id", "left").join(tickets, "customer_id", "left").fillna({
        "completed_orders": 0, "total_revenue": 0.0, "total_sessions": 0, "converted_sessions": 0,
        "avg_pages_viewed": 0.0, "emails_sent": 0, "emails_opened": 0, "emails_clicked": 0,
        "support_tickets": 0, "open_tickets": 0
    }).withColumn(
        "customer_segment",
        F.when(F.col("total_revenue") >= 2000, "High value")
         .when(F.col("total_revenue") >= 700, "Mid value")
         .when(F.col("completed_orders") > 0, "Low value")
         .otherwise("No purchase")
    ).withColumn(
        "churn_risk_flag",
        F.when((F.col("completed_orders") == 0) & (F.col("total_sessions") > 3), 1)
         .when((F.col("open_tickets") > 0) & (F.col("avg_satisfaction_score") <= 2), 1)
         .otherwise(0)
    )

    marketing_performance = campaigns.join(orders, "campaign_id", "left").join(order_items, "order_id", "left").groupBy(
        "campaign_id", "campaign_name", "channel", "budget", "target_region"
    ).agg(
        F.countDistinct("order_id").alias("attributed_orders"),
        F.round(F.sum("net_amount"), 2).alias("attributed_revenue")
    ).fillna({"attributed_orders": 0, "attributed_revenue": 0.0}).withColumn("roas", F.round(F.col("attributed_revenue") / F.col("budget"), 2))

    for name, df in [
        ("dim_customer", dim_customer), ("dim_product", dim_product), ("dim_campaign", dim_campaign),
        ("fact_orders", fact_orders), ("fact_web_sessions", web_sessions), ("fact_email_events", email_events),
        ("fact_support_tickets", support_tickets), ("customer_analytics", customer_analytics),
        ("marketing_performance", marketing_performance)
    ]:
        write_gold(df, name)

    spark.stop()

if __name__ == "__main__":
    build_gold()
