import os
import json
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Explicitly find the .env file
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, '.env')
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")

print("\n" + "="*40)
print("🔍 CODE GURU - AI SYSTEM CHECK")
if api_key:
    print(f"✅ API Key Loaded! (Starts with: {api_key[:6]}...)")
else:
    print(f"❌ API Key NOT FOUND!")
print("="*40 + "\n")

model_name = "gemini-1.5-flash-latest"

try:
    llm = ChatGoogleGenerativeAI(
        model=model_name, 
        temperature=0.3,
        google_api_key=api_key
    )
except Exception as e:
    llm = None

# --- SMART MOCK DATA FOR DEMO SAFETY ---
def get_smart_fallback(student_id, error_type, code_snippet):
    return {
        "issue": f"Logical Constraint Issue: {error_type}",
        "explanation": f"Hello {student_id}, we noticed you've been struggling with your logic. In Java, array boundaries are strict. An array of length 'n' only has valid indices from 0 up to 'n-1'. Your code: '{code_snippet}' tries to force the loop beyond this boundary.",
        "exampleCode": "int[] arr = {10, 20, 30};\n\n// ❌ Incorrect:\n// for (int i = 0; i <= arr.length; i++)\n\n// ✅ Correct Way:\nfor (int i = 0; i < arr.length; i++) {\n    System.out.println(arr[i]);\n}",
        "videoUrl": "https://www.youtube.com/results?search_query=java+array+out+of+bounds+exception",
        "referenceLink": "https://docs.oracle.com/javase/tutorial/java/nutsandbolts/arrays.html",
        "hint": "Analyze your loop condition. Should you use '<=' which includes the length, or just '<'?"
    }

def generate_real_lesson(student_id: str, error_type: str, code_snippet: str):
    if not api_key:
        return get_smart_fallback(student_id, error_type, code_snippet)

    # UPDATED PROMPT: Requesting exampleCode, videoUrl, and referenceLink
    prompt_template = """
    You are 'Code Guru', an expert computer science tutor for first-year IT students.
    A student (ID: {student_id}) has made the following logical error 3 times in Java:
    Error Type: {error_type}
    Code Snippet: {code_snippet}

    Provide the response in the following structured JSON format exactly. Do not output any markdown formatting, just the raw JSON:
    {{
        "issue": "A brief 1-sentence title of the core issue",
        "explanation": "A pedagogical explanation of why this concept happens in Java.",
        "exampleCode": "Write a brief Java code snippet showing the INCORRECT way as a comment, and the CORRECT way underneath it.",
        "videoUrl": "Provide a relevant YouTube search URL, e.g., https://www.youtube.com/results?search_query=java+loop+boundaries",
        "referenceLink": "Provide a relevant documentation link, e.g., https://docs.oracle.com/javase/tutorial/java/nutsandbolts/for.html",
        "hint": "A guiding question or hint to help them fix the code themselves"
    }}
    """

    prompt = PromptTemplate(
        input_variables=["student_id", "error_type", "code_snippet"],
        template=prompt_template
    )
    
    formatted_prompt = prompt.format(student_id=student_id, error_type=error_type, code_snippet=code_snippet)
    content = ""

    try:
        response = llm.invoke(formatted_prompt)
        content = response.content
        print("✅ Generation Success: Using LangChain")
    except Exception as e:
        print(f"\n⚠️ LangChain Failed: {e}")
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts": [{"text": formatted_prompt}]}], "generationConfig": {"temperature": 0.3}}
            res = requests.post(url, headers=headers, json=data)
            if res.status_code == 200:
                content = res.json()['candidates'][0]['content']['parts'][0]['text']
                print("✅ Generation Success: Using Direct REST API")
            else:
                raise Exception(f"Google API Error: {res.text}")
        except Exception as fallback_error:
            return get_smart_fallback(student_id, error_type, code_snippet)

    try:
        content = content.replace("```json", "").replace("```", "").strip()
        start_index = content.find('{')
        end_index = content.rfind('}')
        if start_index != -1 and end_index != -1:
            clean_json = content[start_index:end_index+1]
            return json.loads(clean_json)
        else:
            return get_smart_fallback(student_id, error_type, code_snippet)
    except Exception as parse_error:
        return get_smart_fallback(student_id, error_type, code_snippet)