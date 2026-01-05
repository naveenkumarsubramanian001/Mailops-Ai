import json
import sqlite3
import uuid
from datetime import datetime

# Local Modules
from llm.phi3 import ask_phi3
from rag.retrieve import retrieve_context
from document_verifier import verify_documents
from email_service.sender import send_to_admin

DB_PATH = "db/db.sqlite3"

# --- Step 2: Categorize & Summarize ---
def classify_and_summarize(email: dict) -> dict:
    prompt = f"""
Classify the email intent as one of:
medical_leave, personal_leave, issue, suggestion, information

Summarize the email in 3–5 lines.

Email Subject:
{email['subject']}

Email Body:
{email['body']}

Respond ONLY in JSON with keys: intent, summary
"""
    # API Call
    response = ask_phi3(system="Return strict JSON.", user=prompt)
    
    # Robust JSON extraction
    clean_response = response.replace("```json", "").replace("```", "").strip()
    
    # Try to find the JSON object
    start = clean_response.find("{")
    end = clean_response.rfind("}")
    
    if start != -1 and end != -1:
        clean_response = clean_response[start:end+1]
    
    try:
        return json.loads(clean_response)
    except json.JSONDecodeError:
        # Fallback if specific extraction failed or model hallucinated
        return {"intent": "information", "summary": "Failed to classify."}


# --- Step 3: Check Document Requirements ---
def check_document_requirement(intent: str) -> bool:
    # Define intents that strictly require documents
    required_docs = ["medical_leave", "issue"]
    return intent in required_docs


# --- Step 5: RAG Retrieval (Data Gathering) ---
def get_employee_context(sender_email: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT e.name, e.department, l.sick_used, l.sick_total
        FROM employees e
        JOIN leave_balance l ON e.employee_id = l.employee_id
        WHERE e.email = ?
    """, (sender_email,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"error": "Employee not found"}

    return {
        "name": row[0],
        "department": row[1],
        "sick_used": row[2],
        "sick_total": row[3]
    }


# --- Step 7: Generate Admin Email ---
def generate_admin_email(context: dict) -> str:
    # Unpact context
    email = context['email']
    classification = context['classification']
    employee = context['employee']
    trust_info = context['trust_info']
    policy = context['policy']
    doc_required = context['doc_required']

    # Format Trust Block
    trust_block = "No document verification required."
    if doc_required: 
        if trust_info:
            trust_block = (
                f"Trust Score: {trust_info.get('trust_score', 0)}\n"
                f"Verdict: {trust_info.get('verdict', 'Unknown')}\n"
                f"Issues: {trust_info.get('reasons', [])}"
            )
        else:
             trust_block = "⚠️ MISSING REQUIRED DOCUMENTS: No attachment provided."

    prompt = f"""
You are an HR Operations Assistant.
Draft a professional internal email to the HR Admin regarding a new employee request.

Employee Details:
Name: {employee.get('name', 'Unknown')}
Department: {employee.get('department', 'Unknown')}
Leave Balance (Sick): {employee.get('sick_used', '?')}/{employee.get('sick_total', '?')} used

Request Overview:
{classification['summary']}

Document Verification Report:
{trust_block}

Relevant Policy Snippet:
{policy}

Your Email Must Include:
1. Subject Line: [Action Required] <Subject>
2. Executive Summary of the request.
3. **Verification Findings**: Explicitly state the Verdict (Genuine/Fake) and Trust Score (if applicable).
4. **Evidence**: You MUST copy the EXACT evidence lines from the "Document Verification Report" (e.g., "[P1 L3] Patient Name..."). DO NOT invent lines.
5. Policy Compliance Check based on the retrieved policy.
6. Recommended Action (Approve/Reject/Verify Manually).

Draft the email now.
"""

    return ask_phi3(
        system="Write detailed professional HR emails.",
        user=prompt
    )


# --- Step 9: Logging ---
def log_email(email, intent):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO email_logs VALUES (?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        email["from"],
        intent,
        datetime.utcnow().isoformat(),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


# === MAIN WORKFLOW ===
def process_email(email: dict) -> str:
    # 1. Receive Email (Passed as arg)
    print(f"DEBUG: Processing email from {email['from']}")

    # 2. Categorize & Summarize
    classification = classify_and_summarize(email)
    print(f"DEBUG: Intent detected: {classification['intent']}")

    # 3. Check Document Requirements
    doc_required = check_document_requirement(classification["intent"])
    
    # 4. Verifies documents (if present)
    trust_info = None
    if email.get("attachments"):
        print("DEBUG: Verifying attachments...")
        trust_info = verify_documents(email["attachments"], classification["intent"])
    elif doc_required:
        print("DEBUG: Required documents missing.")

    # 5. RAG Retrieval (Get necessary data)
    employee = get_employee_context(email["from"])
    policy = retrieve_context(classification["intent"], email)

    # 6. Combine all information
    context = {
        "email": email,
        "classification": classification,
        "doc_required": doc_required,
        "trust_info": trust_info,
        "employee": employee,
        "policy": policy
    }

    # 7. Generate Admin-Ready Email
    admin_email_content = generate_admin_email(context)

    # 8. Send Email to Admin
    send_to_admin(admin_email_content)

    # 9. Log everything
    log_email(email, classification["intent"])

    return admin_email_content
