from document_verifier.ocr import extract_text
from document_verifier.verifier import verify_with_llm

def verify_documents(attachments: list, intent: str = "general") -> dict:
    if not attachments:
        return None

    combined_text = ""
    for att in attachments:
        combined_text += f"\n--- File: {att['filename']} ---\n"
        combined_text += extract_text(att["path"]) + "\n"

    # Limit text length to avoid token limits if necessary
    analysis = verify_with_llm(combined_text[:3000], intent)
    print(f"DEBUG: Verifier Analysis: {analysis}")
    
    return {
        "trust_score": analysis.get("confidence", 0),
        "verdict": analysis.get("verdict", "Unknown"),
        "reasons": analysis.get("evidence", []),
        "summary": analysis.get("summary", "")
    }
