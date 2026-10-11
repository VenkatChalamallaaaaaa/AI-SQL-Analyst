import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from agent_tools import get_schema, run_sql, make_chart
tools = [get_schema, run_sql, make_chart]
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

def as_text(content):
    if isinstance(content, str):
        return content
    return "".join(b["text"] for b in content
                   if isinstance(b, dict) and b.get("type") == "text")


llm = init_chat_model(os.environ["MODEL"], timeout=60, max_retries=2).bind_tools(tools)

SYSTEM = SystemMessage(
    "You are a data analyst for a PostgreSQL database of Brazilian e-commerce orders. "
    "Call get_schema first if you are unsure about tables or columns. "
    "Write one SELECT query at a time and run it with run_sql. "
    "If a query errors, read the error, fix the SQL, and retry. "
    "Then answer in plain English using the actual numbers."
    "When the user asks for a chart, graph or trend, use make_chart and tell them the file path."
)

def agent(state: MessagesState):
    return {"messages": [llm.invoke([SYSTEM] + state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
graph = builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "demo-1"}}
    while True:
        question = input("\nYou: ")
        if question.strip().lower() in ("exit", "quit"):
            break
        print("\nAgent: ", end="", flush=True)
        for chunk, meta in graph.stream(
            {"messages": [("user", question)]}, config, stream_mode="messages"
        ):
            if meta.get("langgraph_node") == "agent" and chunk.type == "AIMessageChunk":
                print(as_text(chunk.content), end="", flush=True)
        print()