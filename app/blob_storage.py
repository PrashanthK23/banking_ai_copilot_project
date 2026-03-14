from __future__ import annotations

import os
import pickle
import tempfile
from pathlib import Path
from typing import Optional

from azure.storage.blob import BlobServiceClient
from langchain_community.vectorstores import FAISS

def get_blob_service_client():
    """Get Azure Blob Storage client"""
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not set")
    return BlobServiceClient.from_connection_string(connection_string)

CONTAINER_NAME = "banking-ai-data"

def upload_policy_to_blob(policy_text: str) -> None:
    """Upload policy text to blob storage"""
    blob_service_client = get_blob_service_client()
    
    # Create container if it doesn't exist
    try:
        blob_service_client.create_container(CONTAINER_NAME)
    except Exception:
        pass  # Container might already exist
    
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME, 
        blob="bank_policy.txt"
    )
    blob_client.upload_blob(policy_text, overwrite=True)

def download_policy_from_blob() -> str:
    """Download policy text from blob storage"""
    blob_service_client = get_blob_service_client()
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME, 
        blob="bank_policy.txt"
    )
    
    if not blob_client.exists():
        raise FileNotFoundError("Policy file not found in blob storage")
    
    downloader = blob_client.download_blob()
    return downloader.readall().decode("utf-8")

def upload_vector_store_to_blob(vector_store: FAISS) -> None:
    """Upload FAISS vector store to blob storage"""
    blob_service_client = get_blob_service_client()
    
    # Create container if it doesn't exist
    try:
        blob_service_client.create_container(CONTAINER_NAME)
    except Exception:
        pass
    
    # Save vector store to a temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        vector_path = Path(tmpdir) / "vector_store"
        vector_store.save_local(str(vector_path))
        
        # Upload all files in the directory
        for file_path in vector_path.glob("*"):
            with open(file_path, "rb") as f:
                blob_client = blob_service_client.get_blob_client(
                    container=CONTAINER_NAME, 
                    blob=f"vector_store/{file_path.name}"
                )
                blob_client.upload_blob(f, overwrite=True)

def download_vector_store_from_blob() -> Optional[FAISS]:
    """Download FAISS vector store from blob storage"""
    try:
        blob_service_client = get_blob_service_client()
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            vector_path = Path(tmpdir) / "vector_store"
            vector_path.mkdir(exist_ok=True)
            
            # List and download all vector store blobs
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)
            blobs = container_client.list_blobs(name_starts_with="vector_store/")
            
            downloaded = False
            for blob in blobs:
                blob_client = container_client.get_blob_client(blob.name)
                file_name = blob.name.replace("vector_store/", "")
                file_path = vector_path / file_name
                
                with open(file_path, "wb") as f:
                    downloader = blob_client.download_blob()
                    f.write(downloader.readall())
                downloaded = True
            
            if not downloaded:
                return None
            
            # Use Azure OpenAI embeddings for loading
            from langchain_openai import AzureOpenAIEmbeddings
            embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                deployment=os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT_NAME"),
            )
            
            return FAISS.load_local(str(vector_path), embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Error downloading vector store from blob: {e}")
        return None