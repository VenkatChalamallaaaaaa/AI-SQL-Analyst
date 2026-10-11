import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
llm = init_chat_model(os.environ["MODEL"])

def as_text(content):
    if isinstance(content, str):
        return content
    return "".join(b["text"] for b in content if isinstance(b, dict) and b.get("type") == "text")

print(as_text(llm.invoke("What is a SQL JOIN? Answer in one sentence.").content))
