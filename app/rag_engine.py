from __future__ import annotations

import os
import tempfile

from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings  # Change imports
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.prompts import RAG_ANSWER_PROMPT
from app.blob_storage import download_policy_from_blob, upload_vector_store_to_blob, download_vector_store_from_blob


def _load_policy_text() -> str:
    # Download from Azure Blob Storage
    return download_policy_from_blob()


def _build_vector_store() -> FAISS:
    text = _load_policy_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks]
    
    # Use Azure OpenAI embeddings
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        deployment=os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT_NAME"),
    )
    
    vector_store = FAISS.from_documents(docs, embeddings)
    
    # Upload to blob storage for persistence
    try:
        upload_vector_store_to_blob(vector_store)
    except Exception as e:
        print(f"Warning: Could not upload vector store to blob: {e}")
    
    return vector_store


_VECTOR_STORE: FAISS | None = None


def get_vector_store() -> FAISS:
    global _VECTOR_STORE
    if _VECTOR_STORE is None:
        # Try to download from blob first
        _VECTOR_STORE = download_vector_store_from_blob()
        if _VECTOR_STORE is None:
            _VECTOR_STORE = _build_vector_store()
    return _VECTOR_STORE


@tool
def search_internal_policy(question: str) -> str:
    """Search internal banking policy using RAG. Use this for KYC, disputes, waivers, eligibility, and policy questions."""
    vector_store = get_vector_store()
    docs = vector_store.similarity_search(question, k=3)
    context = "\n\n".join(doc.page_content for doc in docs)

    # Use Azure OpenAI for completion
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0,
    )
    
    prompt = RAG_ANSWER_PROMPT.format(question=question, context=context)
    response = llm.invoke(prompt)
    return response.content