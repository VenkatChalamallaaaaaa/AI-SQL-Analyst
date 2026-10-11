import os, time
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from agent_tools import run_sql, get_schema

load_dotenv()
tools = [get_schema, run_sql]
llm = init_chat_model(os.environ["MODEL"], timeout=60, max_retries=2).bind_tools(tools)

t = time.time()
r = llm.invoke("How many orders are in the orders table?")
print(round(time.time() - t, 1), "seconds")
print(r.tool_calls)