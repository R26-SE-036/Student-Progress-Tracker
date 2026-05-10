import os
import joblib
import pandas as pd

# Define paths to load the trained model
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "models", "cognitive_model.pkl")

# Load the trained Random Forest model into memory
try:
    rf_model = joblib.load(model_path)
    print("✅ ML Model Loaded Successfully!")
except Exception as e:
    print(f"⚠️ Warning: ML Model could not be loaded: {e}")
    rf_model = None

def extract_code_complexity(code_snippet: str) -> int:
    """
    Java-specific feature extraction.
    Counts loops, conditions, and operators to calculate a Complexity Score.
    """
    complexity = 0
    code = code_snippet.lower()
    
    # Extract structural features from Java code
    complexity += code.count("for") * 2
    complexity += code.count("while") * 2
    complexity += code.count("if") * 2
    complexity += code.count("else") * 1
    complexity += code.count("=") * 1
    complexity += code.count("&&") * 1
    complexity += code.count("||") * 1
    complexity += code.count("[") * 1 # Arrays
    
    if complexity == 0:
        complexity = 2
        
    # Ensure the score stays within our model's trained range (1 to 20)
    return max(1, min(complexity, 20))

def predict_cognitive_state(error_count: int, code_snippet: str, past_score: int) -> str:
    if rf_model is None:
        return "Needs Simple Basics"
        
    # 1. Feature Extraction
    complexity_score = extract_code_complexity(code_snippet)
    
    # 2. Prepare features as a Pandas DataFrame
    features = pd.DataFrame(
        [[error_count, complexity_score, past_score]], 
        columns=['error_count', 'complexity_score', 'past_score']
    )
    
    try:
        # 3. Model Prediction
        prediction = rf_model.predict(features)[0]
        print(f"🧠 ML Prediction -> Cognitive State: {prediction} | Complexity Score: {complexity_score}")
        return prediction
    except Exception as e:
        print(f"❌ Prediction Error: {e}")
        return "Needs Simple Basics"