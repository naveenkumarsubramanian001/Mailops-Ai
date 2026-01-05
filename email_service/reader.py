import datetime

# Global flag to simulate "new" emails causing a trigger only once
_has_triggered = False

def read_unread_emails():
    global _has_triggered
    
    # Return empty if already triggered (to avoid infinite loop in main.py)
    if _has_triggered:
        return []

    print("📥 [DUMMY MODE] Simulating incoming email...")
    _has_triggered = True

    # Dummy Email Object
    return [{
        "from": "arjun@aurex.com",
        "subject": "Medical Leave Request",
        "body": "Hi, I have a viral infection and need leave for 3 days. Attached is the certificate.",
        "attachments": [
            {
                "filename": "dummy_medical_report.pdf",
                "path": "mock_path.pdf",  # The verifier mocks OCR anyway
                "mime": "application/pdf"
            }
        ]
    }]

