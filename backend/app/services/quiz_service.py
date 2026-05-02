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
model_name = "gemini-flash-latest"

# Initialize LangChain AI Model
try:
    llm = ChatGoogleGenerativeAI(
        model=model_name, 
        temperature=0.3,
        google_api_key=api_key
    )
except Exception as e:
    llm = None

# Smart Mock Data (Used if AI fails or returns bad format)
def get_smart_quiz_fallback(error_type):
    return [
        {
            "question": f"When dealing with '{error_type}', what is the maximum valid index for an array of size 'n'?",
            "options": ["n", "n + 1", "n - 1", "0"],
            "correct_answer": "n - 1",
            "explanation": "In Java, arrays are zero-indexed, meaning the indices range from 0 to n-1."
        },
        {
            "question": "Which of the following loop conditions correctly prevents an Out Of Bounds error?",
            "options": ["i <= arr.length", "i < arr.length", "i == arr.length", "i > arr.length"],
            "correct_answer": "i < arr.length",
            "explanation": "Using '<' ensures the loop stops before reaching the array's length, which is an invalid index."
        }
    ]

# Validator to fix AI hallucinations and ensure strict JSON format
def validate_and_format_quiz(data, error_type):
    try:
        # If AI wrapped the array in a dictionary
        if isinstance(data, dict):
            if "questions" in data:
                data = data["questions"]
            elif "quiz" in data:
                data = data["quiz"]
            else:
                return get_smart_quiz_fallback(error_type)
        
        # Must be a list
        if not isinstance(data, list) or len(data) == 0:
            return get_smart_quiz_fallback(error_type)
            
        # Check inner objects
        for q in data:
            if not isinstance(q, dict):
                return get_smart_quiz_fallback(error_type)
                
            # Fix alternative keys AI might use
            if "choices" in q and "options" not in q:
                q["options"] = q["choices"]
            if "answer" in q and "correct_answer" not in q:
                q["correct_answer"] = q["answer"]
                
            # Ensure 'options' exists and is a list
            if "options" not in q or not isinstance(q["options"], list):
                return get_smart_quiz_fallback(error_type)
                
        return data
    except Exception as e:
        print(f"❌ Validation Error: {e}")
        return get_smart_quiz_fallback(error_type)

def generate_validation_quiz(student_id: str, error_type: str, code_snippet: str):
    if not api_key:
        return get_smart_quiz_fallback(error_type)

    # Prompt setup
    prompt_template = """
    You are 'Code Guru', an expert computer science tutor.
    A student is struggling with: {error_type}.
    Their code: {code_snippet}

    Generate exactly 4 multiple choice questions to test their understanding.
    Return the response EXACTLY as a JSON array of objects. Do not use markdown.
    [
        {{
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option B",
            "explanation": "Explanation of why Option B is correct."
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
        
        # 2. Try Direct API
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

    # 3. Parse and Validate JSON
    try:
        parsed_data = None
        if isinstance(content, list):
            parsed_data = content
        elif isinstance(content, dict):
            parsed_data = content
        elif isinstance(content, str):
            content = content.replace("```json", "").replace("```", "").strip()
            start_index = content.find('[')
            end_index = content.rfind(']')
            
            if start_index != -1 and end_index != -1:
                clean_json = content[start_index:end_index+1]
                parsed_data = json.loads(clean_json)
            else:
                # Fallback if it's a dict format
                start_idx_dict = content.find('{')
                end_idx_dict = content.rfind('}')
                if start_idx_dict != -1 and end_idx_dict != -1:
                    clean_json = content[start_idx_dict:end_idx_dict+1]
                    parsed_data = json.loads(clean_json)
        
        if parsed_data is not None:
            return validate_and_format_quiz(parsed_data, error_type)
        else:
            return get_smart_quiz_fallback(error_type)

    except Exception as parse_error:
        print(f"❌ Quiz JSON Parsing Error: {parse_error}")
        return get_smart_quiz_fallback(error_type)