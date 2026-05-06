import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Define the directory to save the trained model
base_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(base_dir, "models")
model_path = os.path.join(model_dir, "cognitive_model.pkl")

# Create the models directory if it does not exist
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

def generate_synthetic_data(num_samples=1000):
    """
    Generates dummy data to train our Random Forest model.
    Since we do not have thousands of real students yet, this acts as our dataset.
    """
    np.random.seed(42)
    
    # 1. error_count: Number of times the student failed (1 to 10)
    error_counts = np.random.randint(1, 11, num_samples)
    
    # 2. complexity_score: AST calculated complexity of the code (1 to 20)
    complexity_scores = np.random.randint(1, 21, num_samples)
    
    # 3. past_score: The student's previous score from Neo4j DB (0 to 100)
    past_scores = np.random.randint(0, 101, num_samples)
    
    # Generate the target labels based on logical conditions
    labels = []
    for i in range(num_samples):
        errors = error_counts[i]
        complexity = complexity_scores[i]
        past = past_scores[i]
        
        # Logic to assign Cognitive Load
        if errors > 5 and complexity > 10 and past < 50:
            labels.append("High Cognitive Load")
        elif errors > 3 and past >= 50:
            labels.append("Needs Simple Basics")
        elif errors <= 3 and complexity <= 10:
            labels.append("Minor Syntax Error")
        else:
            labels.append("Needs Simple Basics")
            
    # Create a Pandas DataFrame
    data = pd.DataFrame({
        'error_count': error_counts,
        'complexity_score': complexity_scores,
        'past_score': past_scores,
        'cognitive_state': labels
    })
    
    return data

def train_and_save_model():
    """
    Trains the Random Forest model and saves it as a .pkl file.
    """
    print("⏳ Generating synthetic data...")
    dataset = generate_synthetic_data(1500)
    
    # Separate features (X) and target label (y)
    X = dataset[['error_count', 'complexity_score', 'past_score']]
    y = dataset['cognitive_state']
    
    # Split data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("⏳ Training Random Forest Classifier...")
    # Initialize and train the model
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Test the accuracy of the model
    predictions = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"✅ Model trained successfully! Accuracy: {accuracy * 100:.2f}%")
    
    # Save the trained model to a file
    joblib.dump(rf_model, model_path)
    print(f"✅ Model saved at: {model_path}")

if __name__ == "__main__":
    print("🚀 Starting ML Model Training Process...")
    train_and_save_model()