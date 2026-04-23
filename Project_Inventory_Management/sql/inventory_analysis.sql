--Query 1 — Top selling products:

SELECT 
    p.product_category_name,
    COUNT(oi.order_id) AS total_orders,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_orders DESC
LIMIT 15;

--Query 2 — Slow moving / dead stock products:

SELECT 
    p.product_category_name,
    COUNT(DISTINCT oi.product_id) AS unique_products,
    COUNT(oi.order_id) AS total_orders,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_orders ASC
LIMIT 15;

--Query 3 — Revenue concentration by category:

SELECT 
    ct.product_category_name_english AS category,
    COUNT(oi.order_id) AS total_orders,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(100.0 * SUM(oi.price) / SUM(SUM(oi.price)) OVER(), 2) AS revenue_percentage
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY ct.product_category_name_english
ORDER BY total_revenue DESC
LIMIT 15;