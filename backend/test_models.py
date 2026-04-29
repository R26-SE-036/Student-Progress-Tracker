import os
import requests
from dotenv import load_dotenv

# Load the .env file
load_dotenv('.env')
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key not found in .env file!")
else:
    print("🔍 Fetching available models for your API Key...\n")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ AVAILABLE MODELS:")
        for model in data.get('models', []):
            print(f" - {model['name']}")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)