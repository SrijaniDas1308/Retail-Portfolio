-- Query 1 → total customers count

SELECT COUNT(*) AS total_customers 
FROM customers;

--Query 2 → which state has the most customers

SELECT customer_state, 
       COUNT(*) AS total_customers
FROM customers
GROUP BY customer_state
ORDER BY total_customers DESC
LIMIT 10;

--Query 3 → total revenue number

SELECT ROUND(SUM(payment_value)::numeric, 2) AS total_revenue
FROM order_payments;

--Query 4 → top city

SELECT customer_city,
       customer_state,
       COUNT(*) AS total_customers
FROM customers
GROUP BY customer_city, customer_state
ORDER BY total_customers DESC
LIMIT 10;
