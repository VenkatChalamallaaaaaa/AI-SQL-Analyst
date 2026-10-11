import time, uuid
from sqlalchemy import text
from agent_tools import engine
from agent import graph, as_text

# (question, SQL returning ONE value that must appear in the answer)
CASES = [
        ("Which product category in English has the highest total revenue?",
     "SELECT t.product_category_name_english FROM order_items i JOIN orders o USING (order_id) JOIN products p USING (product_id) JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name WHERE o.order_status NOT IN ('canceled','unavailable') GROUP BY 1 ORDER BY SUM(i.price) DESC LIMIT 1"),
    ("What is the total revenue (product price only) across all orders?",
     "SELECT ROUND(SUM(i.price)::numeric, 0) FROM order_items i JOIN orders o USING (order_id) WHERE o.order_status NOT IN ('canceled','unavailable')"),
    ("What is the average delivery time in days for delivered orders, rounded to 1 decimal?",
     "SELECT ROUND(AVG(EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp))/86400)::numeric, 1) FROM orders WHERE order_delivered_customer_date IS NOT NULL"),
    ("Which seller has the highest total sales by product price?",
     "SELECT i.seller_id FROM order_items i JOIN orders o USING (order_id) WHERE o.order_status NOT IN ('canceled','unavailable') GROUP BY 1 ORDER BY SUM(i.price) DESC LIMIT 1"),
    ("How many orders were delivered later than their estimated delivery date?",
     "SELECT COUNT(*) FROM orders WHERE order_delivered_customer_date > order_estimated_delivery_date"),
    ("Which customer (by unique id) spent the most in total payments?",
     "SELECT c.customer_unique_id FROM customers c JOIN orders o USING (customer_id) JOIN order_payments p USING (order_id) GROUP BY 1 ORDER BY SUM(p.payment_value) DESC LIMIT 1"),
]

def expected_value(sql):
    with engine.connect() as conn:
        v = conn.execute(text(sql)).scalar()
    return v

def variants(v):
    """Ways the number might be written in the answer."""
    if isinstance(v, (int,)) or (hasattr(v, "is_integer") and float(v).is_integer()):
        n = int(v)
        return [str(n), f"{n:,}"]
    return [str(v)]

passed = 0
for q, sql in CASES:
    exp = expected_value(sql)
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    start = time.time()
    try:
        result = graph.invoke({"messages": [("user", q)]}, config)
        answer = as_text(result["messages"][-1].content)
    except Exception as e:
        answer = f"ERROR: {e}"
    ok = any(x.lower() in answer.lower() for x in variants(exp))
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'}  ({time.time()-start:.0f}s)  {q}")
    if not ok:
        print(f"      expected: {exp}\n      got: {answer[:200]}")

print(f"\nScore: {passed}/{len(CASES)}")