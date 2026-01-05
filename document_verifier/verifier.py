import json
from llm.phi3 import ask_phi3

def verify_with_llm(ocr_text: str, intent: str) -> dict:
    prompt = f"""
You are a Document Verification Expert.
Analyze the following document text for the claimed intent: '{intent}'.

Document Text:
{ocr_text}

Tasks:
1. Identify the Document Type (e.g., Medical Cert, Invoice, Email, Invitation).
2. Assess Originality: Look for consistency, formal language, and required details.
3. Extract Evidence: Cite specific lines (e.g., [L12]) that support your findings.
4. Verdict: "Genuine" or "Fake/Suspicious".

Respond ONLY in JSON format:
{{
  "document_type": "...",
  "is_original_likely": true/false,
  "verdict": "...",
  "confidence": 0-100,
  "summary": "...",
  "evidence": ["line quoted", ...]
}}

IMPORTANT: Ensure all strings are valid JSON (escape quotes). Do not add comments.
"""
    try:
        response = ask_phi3(system="Return strict JSON.", user=prompt)
        # Attempt to clean potential markdown code blocks
        clean_response = response.replace("```json", "").replace("```", "").strip()
        
        # Robust extraction: find first { and last }
        start = clean_response.find("{")
        end = clean_response.rfind("}")
        if start != -1 and end != -1:
            clean_response = clean_response[start:end+1]
            
        return json.loads(clean_response)
    except Exception as e:
        return {
            "document_type": "Unknown",
            "is_original_likely": False,
            "verdict": "Error processing document",
            "confidence": 0,
            "summary": f"Failed to analyze document: {str(e)}",
            "evidence": []
        }
