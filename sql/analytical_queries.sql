-- Example analytical queries for the Gold layer after loading outputs into a SQL warehouse.

-- Monthly revenue
SELECT order_month, SUM(net_amount) AS total_revenue, COUNT(DISTINCT order_id) AS total_orders
FROM fact_orders
WHERE order_status = 'Completed'
GROUP BY order_month
ORDER BY order_month;

-- Customer segments
SELECT customer_segment, COUNT(*) AS customers, SUM(total_revenue) AS revenue
FROM customer_analytics
GROUP BY customer_segment
ORDER BY revenue DESC;

-- Campaign ROAS
SELECT campaign_id, campaign_name, channel, budget, attributed_revenue, roas
FROM marketing_performance
ORDER BY roas DESC;
