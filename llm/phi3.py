import requests
import json

def ask_phi3(system, user):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "mailops-hr",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "stream": False
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["message"]["content"]
    return f"Error: {response.text}"
