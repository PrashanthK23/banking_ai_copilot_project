# Banking AI Copilot (Simple GenAI + RAG + Agentic AI + MCP)

A very small demo project for the **banking domain**.

## Real-time use case
**Retail Banking Relationship Manager Copilot**

This assistant helps a bank executive answer customer questions such as:
- Is this customer eligible for a personal loan top-up?
- What EMI would the customer pay?
- What internal policy says about KYC, late fees, or card disputes?
- What is the latest public information from the web for a market or regulatory topic?

## What this project includes
- **GenAI** using OpenAI
- **RAG** over a small internal banking policy document
- **Agentic AI** using a LangChain agent
- **MCP tool** using a local FastMCP server
- **Prompt engineering** through reusable prompts
- **Optional web search** using `serper.dev`
- **Streamlit UI**

## Why this use case is good for demo
It is practical, easy to explain, and small enough to run with less code.

---

## Folder structure

```bash
banking_ai_copilot_project/
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   └── bank_policy.txt
└── app/
    ├── __init__.py
    ├── prompts.py
    ├── rag_engine.py
    ├── mcp_server.py
    ├── tools.py
    └── agent.py
```

---

## Setup

### 1) Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # mac/linux
.venv\Scripts\activate      # windows
```

### 2) Install packages
```bash
pip install -r requirements.txt
```

### 3) Add environment variables
Create `.env` using `.env.example`

```env
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-mini
SERPER_API_KEY=your_serper_key_optional
```

### 4) Run Streamlit app
```bash
streamlit run app.py
```

---

## Demo questions
Use one of these in the UI:

1. `Can customer CUST1001 get a personal loan top-up?`
2. `What is the EMI for 500000 at 11% for 36 months?`
3. `Explain KYC refresh rules from internal bank policy.`
4. `Summarize latest RBI related update for retail borrowers.`
5. `For customer CUST1003, suggest next best banking action.`

---

## How the flow works
1. User asks question in Streamlit.
2. LangChain agent decides which tool to use.
3. The agent may use:
   - **RAG tool** for internal bank policy
   - **Serper search tool** for live public web info
   - **MCP tools** for customer lookup and EMI calculation
4. Model produces final answer in business-friendly language.

---

## Notes
- This is a **demo project**, not a production banking system.
- Customer data is mocked locally.
- Web search is optional.
- Internal policy data is a simple text file to keep code minimal.

