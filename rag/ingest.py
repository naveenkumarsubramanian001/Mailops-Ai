import os
import chromadb
import os
import chromadb
import docx
import requests

def get_embedding(text):
    url = "http://localhost:11434/api/embeddings"
    payload = {
        "model": "phi3:mini",
        "prompt": text
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["embedding"]
    print(f"Embedding error: {response.text}")
    return []

DB_PATH = "db/chroma_db"
DOCS_DIR = "aurex docx"

from chromadb.config import Settings

def ingest_documents():
    print("Initializing ChromaDB (Legacy)...")
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=DB_PATH
    ))
    
    # Dummy EF to avoid downloading default model
    class DummyEF:
        def __call__(self, input):
            return [[0.0]*384 for _ in input]
            
    collection = client.get_or_create_collection(
        name="policy_rag", 
        embedding_function=DummyEF()
    )

    files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".docx")]
    
    if not files:
        print("No .docx files found to ingest.")
        return

    print(f"Found {len(files)} documents. Starting ingestion...")

    for filename in files:
        file_path = os.path.join(DOCS_DIR, filename)
        try:
            doc = docx.Document(file_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            
            # Simple chunking by 500 characters
            chunk_size = 500
            chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                    
                print(f"Embedding {filename} chunk {i}...")
                embedding = get_embedding(chunk)
                if not embedding:
                    continue
                
                collection.add(
                    ids=[f"{filename}_{i}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"source": filename}]
                )
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    client.persist()
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_documents()
