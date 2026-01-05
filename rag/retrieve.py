import chromadb
import chromadb
import requests
from rag.sql_tool import get_employee_data

def get_embedding(text):
    url = "http://localhost:11434/api/embeddings"
    payload = {
        "model": "phi3:mini",
        "prompt": text
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["embedding"]
    return []

CHROMA_PATH = "db/chroma_db"

from chromadb.config import Settings

def retrieve_context(intent: str, entities: dict) -> str:
    context_parts = []
    
    # 1. Retrieve Static Policy from ChromaDB
    try:
        client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=CHROMA_PATH
        ))
        
        class DummyEF:
            def __call__(self, input):
                return [[0.0]*384 for _ in input]

        collection = client.get_or_create_collection(
            name="policy_rag",
            embedding_function=DummyEF()
        )
        
        # Use intent + optional specific query if available
        query_text = intent
        if entities.get("query_text"):
             query_text += " " + entities["query_text"]

        # Generate embedding for the query
        embedding = get_embedding(query_text)
        results = collection.query(
            query_embeddings=[embedding],
            n_results=2
        )
        
        if results["documents"] and results["documents"][0]:
            context_parts.append(f"--- RELEVANT POLICY ({intent}) ---\n" + "\n".join(results["documents"][0]))
        else:
            context_parts.append(f"--- RELEVANT POLICY ---\nNo specific policy found for '{intent}'.")

    except Exception as e:
        context_parts.append(f"--- POLICY ERROR ---\nFailed to retrieve policy: {str(e)}")

    # 2. Retrieve Transactional Data from SQLite
    employee_email = entities.get("from")
    if employee_email:
        emp_data = get_employee_data(employee_email)
        if emp_data:
            info = (
                f"--- EMPLOYEE CONTEXT ({emp_data['name']}) ---\n"
                f"Department: {emp_data['department']}\n"
                f"Role: {emp_data['role']}\n"
                f"Sick Leave: {emp_data['sick_used']}/{emp_data['sick_total']} used\n"
                f"Casual Leave: {emp_data['casual_used']}/{emp_data['casual_total']} used\n"
            )
            context_parts.append(info)
        else:
            context_parts.append(f"--- EMPLOYEE CONTEXT ---\nEmployee with email {employee_email} not found.")

    return "\n\n".join(context_parts)

# Backward compatibility alias
def retrieve_policy(intent):
    # This is a fallback if orchestrator calls with old signature
    return retrieve_context(intent, {})
