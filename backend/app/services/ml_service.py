import os
import ast
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
    Uses Python's Abstract Syntax Tree (AST) to analyze the student's code.
    Counts loops, conditions, and variables to calculate a Complexity Score.
    """
    complexity = 0
    try:
        # Parse the code into an AST structure
        tree = ast.parse(code_snippet)
        
        # Traverse the tree nodes
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While, ast.If)):
                complexity += 2 # Loops and conditions add more complexity
            elif isinstance(node, (ast.Assign, ast.FunctionDef)):
                complexity += 1 # Variable assignments add minor complexity
                
    except SyntaxError:
        # If the code has major syntax errors and cannot be parsed, assign a default score
        complexity = 5
        
    # Ensure the score stays within our model's trained range (1 to 20)
    return max(1, min(complexity, 20))

def predict_cognitive_state(error_count: int, code_snippet: str, past_score: int) -> str:
    """
    Takes student metrics, extracts code complexity via AST, 
    and uses the Random Forest model to predict the student's cognitive state.
    """
    # Fallback if model is missing
    if rf_model is None:
        return "Needs Simple Basics"
        
    # 1. AST Feature Extraction
    complexity_score = extract_code_complexity(code_snippet)
    
    # 2. Prepare features as a Pandas DataFrame (This fixes the scikit-learn warning!)
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