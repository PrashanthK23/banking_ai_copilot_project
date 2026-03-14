from __future__ import annotations

import asyncio
import os
from pathlib import Path

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import AzureChatOpenAI  # Change import

from app.prompts import SYSTEM_PROMPT
from app.rag_engine import search_internal_policy
from app.tools import serper_web_search

BASE_DIR = Path(__file__).resolve().parent.parent
MCP_SERVER_FILE = BASE_DIR / "app" / "mcp_server.py"


async def _load_all_tools():
    client = MultiServerMCPClient(
        {
            "banking_mcp": {
                "transport": "stdio",
                "command": "python",
                "args": [str(MCP_SERVER_FILE)],
            }
        }
    )
    mcp_tools = await client.get_tools()
    return [search_internal_policy, serper_web_search, *mcp_tools]


async def ask_banking_agent_async(user_query: str) -> str:
    tools = await _load_all_tools()
    
    # Initialize Azure OpenAI client
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0,
    )
    
    agent = create_agent(
        model=llm,  # Pass the Azure client instead of string
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
    result = await agent.ainvoke({"messages": [HumanMessage(content=user_query)]})

    messages = result.get("messages", [])
    if not messages:
        return "No response generated."

    final_message = messages[-1]
    content = getattr(final_message, "content", "")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part)

    return str(content)


def ask_banking_agent(user_query: str) -> str:
    return asyncio.run(ask_banking_agent_async(user_query))