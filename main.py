import time
import sys
import os
from dotenv import load_dotenv

# Ensure local modules are found
sys.path.append(os.getcwd())

from dotenv import load_dotenv
from unittest.mock import MagicMock

# --- DUMMY MODE PATCHES ---
# Since we don't have real files, we must mock the OCR layer here
sys.modules['pytesseract'] = MagicMock()
sys.modules['pdf2image'] = MagicMock()
sys.modules['PIL'] = MagicMock()

import document_verifier
# Force the extractor to return dummy text for ANY file
document_verifier.extract_text = MagicMock(return_value="""[P1 L1] COMMUNITY HOSPITAL
[P1 L2] Date: 2026-01-05
[P1 L3] Patient: Arjun Kumar
[P1 L4] Diagnosis: Severe Viral Infection
[P1 L5] Advice: Bed rest for 3 days.
[P1 L6] Signed, Dr. No
""")

from email_service.reader import read_unread_emails
from orchestrator import process_email

# Load Env
load_dotenv()

def main():
    print("🚀 Mailops AI Service Started...")
    print("📡 Listening for incoming emails (Polling every 10s)...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # 1. Fetch New Emails
            new_emails = read_unread_emails()
            
            if new_emails:
                for email in new_emails:
                    print(f"\n📨 Processing Email from: {email['from']}")
                    
                    try:
                        # 2. Process via Orchestrator
                        process_email(email)
                        print("✅ Email Processed Successfully.")
                    except Exception as e:
                        print(f"❌ Error processing email: {e}")
            
            # Wait before next poll
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛑 Service Stopped by User.")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")

if __name__ == "__main__":
    main()
