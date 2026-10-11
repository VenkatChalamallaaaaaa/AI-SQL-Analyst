Database: PostgreSQL, Brazilian e-commerce orders from Olist.
Data covers Sept 2016 to Oct 2018. Never use today's date; for "last month",
"this year" etc. use the latest date in orders.order_purchase_timestamp.
Data before 2017 is very sparse.

Tables:
- customers(customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
  customer_id is unique PER ORDER. To count real people, use customer_unique_id.
- orders(order_id, customer_id, order_status, order_purchase_timestamp,
  order_approved_at, order_delivered_carrier_date,
  order_delivered_customer_date, order_estimated_delivery_date)
  Delivery time = order_delivered_customer_date - order_purchase_timestamp.
  Delivered date is NULL for undelivered orders.
- order_items(order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value)
- order_payments(order_id, payment_sequential, payment_type, payment_installments, payment_value)
- order_reviews(review_id, order_id, review_score 1-5, review_comment_title,
  review_comment_message, review_creation_date, review_answer_timestamp)
- products(product_id, product_category_name, ...) category names are in Portuguese
- product_category_name_translation(product_category_name, product_category_name_english)
  Join to this to show English category names.
- sellers(seller_id, seller_zip_code_prefix, seller_city, seller_state)
- geolocation(...) very large, rarely needed.

Rules:
- Revenue = SUM(order_items.price). Exclude order_status = 'canceled' for sales questions.
- Money is in Brazilian reais (BRL).
- Customer state codes are Brazilian states (SP, RJ, RR, ...).
- For any question about orders, sales, revenue or customers, exclude order_status = 'canceled'
  and 'unavailable' unless the user asks otherwise. State this in the answer in one short phrase.
- Revenue ALWAYS means SUM(order_items.price) (product price only, no freight).
  Do not offer alternative definitions unless asked. Mention freight only if relevant.
- For rankings by averages (review scores, delivery time), require at least 100 rows per
  group so tiny samples don't win, and state the threshold.