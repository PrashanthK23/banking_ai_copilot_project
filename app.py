from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from app.agent import ask_banking_agent

# Load environment variables
load_dotenv()

# Azure App Service specific configuration
if os.getenv("WEBSITE_SITE_NAME"):  # Running on Azure App Service
    # Configure for Azure
    st.set_page_config(
        page_title="Banking AI Copilot", 
        layout="wide",
        initial_sidebar_state="auto"
    )
else:
    st.set_page_config(page_title="Banking AI Copilot", layout="wide")

st.title("🏦 Banking AI Copilot")
st.caption("Simple GenAI + RAG + Agentic AI + MCP + Prompt Engineering demo")

with st.sidebar:
    st.subheader("Configuration")
    
    # Check Azure OpenAI configuration
    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        st.write(f"Azure OpenAI endpoint: `{os.getenv('AZURE_OPENAI_ENDPOINT').split('/')[-1]}`")
        st.write(f"Deployment: `{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')}`")
    else:
        st.warning("Azure OpenAI not configured")
    
    st.write("Serper search is optional.")
    st.markdown("**Sample customer IDs:** `CUST1001`, `CUST1002`, `CUST1003`")
    
    # Add Azure App Service info if running on Azure
    if os.getenv("WEBSITE_SITE_NAME"):
        st.caption(f"Running on Azure App Service: {os.getenv('WEBSITE_SITE_NAME')}")

sample_query = st.selectbox(
    "Try a sample question",
    [
        "Can customer CUST1001 get a personal loan top-up?",
        "What is the EMI for 500000 at 11% for 36 months?",
        "Explain KYC refresh rules from internal bank policy.",
        "Summarize latest RBI related update for retail borrowers.",
        "For customer CUST1003, suggest next best banking action.",
    ],
)

query = st.text_area("Ask your banking question", value=sample_query, height=120)

if st.button("Run Assistant", use_container_width=True):
    # Check Azure OpenAI configuration
    if not os.getenv("AZURE_OPENAI_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
        st.error("Azure OpenAI credentials are missing. Please configure in your environment variables.")
    else:
        with st.spinner("Thinking..."):
            try:
                answer = ask_banking_agent(query)
                st.success("Response generated")
                st.markdown(answer)
            except Exception as exc:
                st.exception(exc)

st.divider()
st.markdown(
    """
### What is happening behind the scenes?
- **GenAI**: Azure OpenAI model generates the answer.
- **RAG**: Reads internal bank policy from Azure Blob Storage.
- **Agentic AI**: LangChain agent chooses tools.
- **MCP**: Local MCP server exposes customer and EMI tools.
- **Prompt engineering**: Guardrails guide the assistant to stay grounded.
"""
)