import os
import json
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, '.env')
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
model_name = "gemini-1.5-flash-latest"

try:
    llm = ChatGoogleGenerativeAI(
        model=model_name, 
        temperature=0.3,
        google_api_key=api_key
    )
except Exception as e:
    llm = None

# --- SMART MOCK DATA FOR THE QUIZ ---
def get_smart_quiz_fallback(error_type):
    return [
        {
            "question": f"When dealing with '{error_type}', what is the maximum valid index for an array of size 'n'?",
            "options": ["n", "n + 1", "n - 1", "0"],
            "correct_answer": "n - 1",
            "explanation": "In Java, arrays are zero-indexed, meaning the indices range from 0 to n-1."
        },
        {
            "question": "Which of the following loop conditions correctly prevents an Out Of Bounds error for an array named 'arr'?",
            "options": ["i <= arr.length", "i < arr.length", "i == arr.length", "i > arr.length"],
            "correct_answer": "i < arr.length",
            "explanation": "Using '<' ensures the loop stops exactly before reaching 'arr.length'."
        }
    ]

def generate_validation_quiz(student_id: str, error_type: str, code_snippet: str):
    if not api_key:
        return get_smart_quiz_fallback(error_type)

    prompt_template = """
    You are 'Code Guru', an expert computer science tutor for first-year IT students.
    A student (ID: {student_id}) has just read a lesson about this logical error they made in Java:
    Error Type: {error_type}
    Code Snippet: {code_snippet}

    Generate a short Multiple Choice Quiz (exactly 2 questions) to test their understanding of this specific concept.
    Provide the response strictly as a JSON ARRAY of objects. Do not use markdown blocks.
    Format exactly like this:
    [
        {{
            "question": "A clear, concept-focused question?",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answer": "The exact string of the correct option",
            "explanation": "Short explanation of why this is correct"
        }}
    ]
    """

    prompt = PromptTemplate(
        input_variables=["student_id", "error_type", "code_snippet"],
        template=prompt_template
    )
    
    formatted_prompt = prompt.format(student_id=student_id, error_type=error_type, code_snippet=code_snippet)
    content = ""

    # 1. Try LangChain
    try:
        response = llm.invoke(formatted_prompt)
        content = response.content
        print("✅ Quiz Generation: Using LangChain")
    except Exception as e:
        print(f"⚠️ Quiz LangChain Failed: {e}")
        # 2. Direct REST API Fallback
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts": [{"text": formatted_prompt}]}], "generationConfig": {"temperature": 0.3}}
            
            res = requests.post(url, headers=headers, json=data)
            if res.status_code == 200:
                content = res.json()['candidates'][0]['content']['parts'][0]['text']
                print("✅ Quiz Generation: Using Direct API")
            else:
                raise Exception("API Request Failed")
        except Exception as fallback_error:
            print(f"❌ Quiz Ultimate Fallback Failed. Using Mock Data.")
            return get_smart_quiz_fallback(error_type)

    # Parse JSON Array
    try:
        content = content.replace("```json", "").replace("```", "").strip()
        start_index = content.find('[')
        end_index = content.rfind(']')
        
        if start_index != -1 and end_index != -1:
            clean_json = content[start_index:end_index+1]
            return json.loads(clean_json)
        else:
            return get_smart_quiz_fallback(error_type)
    except Exception as parse_error:
        print(f"❌ Quiz JSON Parsing Error: {parse_error}")
        return get_smart_quiz_fallback(error_type)