import os
import json
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.services.rag_service import retrieve_context

# Load environment variables
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

model_name = "gemini-flash-latest"

try:
    llm = ChatGoogleGenerativeAI(
        model=model_name, 
        temperature=0.3,
        google_api_key=api_key
    )
except Exception as e:
    llm = None

def get_smart_fallback(student_id, error_type, code_snippet):
    return {
        "issue": f"Logical Constraint Issue: {error_type}",
        "explanation": f"Hello {student_id}, we noticed you've been struggling with your logic. In Java, array boundaries are strict. An array of length 'n' only has valid indices from 0 up to 'n-1'.",
        "exampleCode": "int[] arr = {10, 20, 30};\n\n// ❌ Incorrect:\n// for (int i = 0; i <= arr.length; i++)\n\n// ✅ Correct Way:\nfor (int i = 0; i < arr.length; i++) {\n    System.out.println(arr[i]);\n}",
        "mermaidDiagram": "graph TD\n    A[Array length 'n'] --> B[Valid: 0 to n-1]\n    A --> C[Invalid: n]\n    C --> D[IndexOutOfBoundsException]\n    style C fill:#FF453A,stroke:#333,stroke-width:2px",
        "videoUrl": "https://www.youtube.com/results?search_query=java+array+out+of+bounds",
        "referenceLink": "https://docs.oracle.com/javase/tutorial/java/nutsandbolts/arrays.html",
        "hint": "Analyze your loop condition. Should you use '<=' or just '<'?"
    }

def generate_real_lesson(student_id: str, error_type: str, code_snippet: str):
    if not api_key:
        return get_smart_fallback(student_id, error_type, code_snippet)

    # RAG Context
    search_query = f"Explain {error_type} and how to fix {code_snippet}"
    retrieved_context = retrieve_context(search_query)

    prompt_template = """
    You are 'Code Guru', an expert computer science tutor for first-year IT students.
    A student (ID: {student_id}) has made this logical error: {error_type}
    Code: {code_snippet}

    === SYLLABUS NOTES ===
    {context}
    ======================

    Generate a micro-lesson. Also, generate a simple 'Mermaid.js' chart (graph TD) that visually models the memory layout or error concept.
    
    Provide the response EXACTLY in this JSON format:
    {{
        "issue": "A brief 1-sentence title",
        "explanation": "A pedagogical explanation.",
        "exampleCode": "Show incorrect code as comment, and correct way underneath.",
        "mermaidDiagram": "graph TD\\n A[Step 1] --> B[Step 2]",
        "videoUrl": "Provide YouTube URL",
        "referenceLink": "Provide Documentation link",
        "hint": "A guiding question"
    }}
    """

    prompt = PromptTemplate(input_variables=["student_id", "error_type", "code_snippet", "context"], template=prompt_template)
    formatted_prompt = prompt.format(student_id=student_id, error_type=error_type, code_snippet=code_snippet, context=retrieved_context)
    
    content = ""

    try:
        response = llm.invoke(formatted_prompt)
        content = response.content
        print("✅ Graph RAG Generation Success: Using LangChain")
    except Exception as e:
        print(f"\n⚠️ LangChain Failed: {e}")
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            data = {"contents": [{"parts": [{"text": formatted_prompt}]}], "generationConfig": {"temperature": 0.3}}
            res = requests.post(url, headers={'Content-Type': 'application/json'}, json=data)
            if res.status_code == 200:
                content = res.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                raise Exception("API Error")
        except Exception:
            return get_smart_fallback(student_id, error_type, code_snippet)

    try:
        if isinstance(content, dict):
            return content
        elif isinstance(content, str):
            content = content.replace("```json", "").replace("```", "").strip()
            start_index = content.find('{')
            end_index = content.rfind('}')
            if start_index != -1 and end_index != -1:
                clean_json = content[start_index:end_index+1].replace("\\n", "\\\\n")
                return json.loads(clean_json)
        return get_smart_fallback(student_id, error_type, code_snippet)
    except Exception as parse_error:
        print(f"❌ JSON Parsing Error: {parse_error}")
        return get_smart_fallback(student_id, error_type, code_snippet)