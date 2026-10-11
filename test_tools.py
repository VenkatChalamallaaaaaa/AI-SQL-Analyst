from agent_tools import get_schema, run_sql

print(get_schema.invoke({})[:200])
print(run_sql.invoke({"query": "SELECT COUNT(*) FROM orders"}))
print(run_sql.invoke({"query": "DROP TABLE orders"}))
print(run_sql.invoke({"query": "SELECT * FROM no_such_table"}))