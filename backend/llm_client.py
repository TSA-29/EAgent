import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_llm(prompt):
    api_key = os.getenv("STEP_API_KEY")
    if not api_key:
        return "Error: STEP_API_KEY not set"

    url = "https://api.stepfun.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "step-3.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error calling LLM: {str(e)}"
