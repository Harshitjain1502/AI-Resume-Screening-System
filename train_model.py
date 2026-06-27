# train_model.py
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Import algorithms for evaluation
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import MultinomialNB

def generate_mock_dataset():
    """Generates a synthetic dataset for resume classification training."""
    data = {
        "text": [
            "python machine learning data science pandas numpy scikit learn developer",
            "java spring boot microservices hibernate backend enterprise software",
            "html css javascript react node express web developer frontend fullstack",
            "aws devops docker kubernetes jenkins ci cd cloud architect linux",
            "sql powerbi tableau data analyst excel data warehouse business intelligence",
            "python django flask postgresql sql backend developer engineer api",
            "machine learning deep learning computer vision nlp tensorflow pytorch ai",
            "project manager agile scrum kanban pmp jira delivery management",
            "hr recruiter talent acquisition onboarding sourcing payroll management",
            "cybersecurity penetration testing firewall network security cissp ethical hacking"
        ] * 10, # Multiply to get 100 rows for stable testing
        "label": [1, 0, 0, 0, 0, 1, 1, 0, 0, 0] * 10 # 1 = Suitable (AI/Data/Python), 0 = Not Suitable
    }
    return pd.DataFrame(data)

def train_and_evaluate():
    print("--- Starting Machine Learning Pipeline ---")
    
    # 1. Load Data
    df = generate_mock_dataset()
    X = df["text"]
    y = df["label"]
    
    # 2. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Feature Engineering: TF-IDF Vectorization
    print("Vectorizing text data using TF-IDF...")
    vectorizer = TfidfVectorizer(max_features=1000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # 4. Define Models to Benchmark
    models = {
        "Logistic Regression": LogisticRegression(),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Support Vector Machine": SVC(probability=True, random_state=42),
        "Naive Bayes": MultinomialNB()
    }
    
    best_model = None
    best_f1 = -1
    best_model_name = ""
    performance_records = []
    
    # 5. Model Evaluation Loop
    print("\nBenchmarking models...")
    for name, model in models.items():
        model.fit(X_train_vec, y_train)
        preds = model.predict(X_test_vec)
        
        # Calculate evaluation metrics
        acc = accuracy_score(y_test, preds)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, average='binary', zero_division=0)
        
        performance_records.append({
            "Model": name, "Accuracy": acc, "Precision": precision, "Recall": recall, "F1-Score": f1
        })
        
        # Keep track of the highest performing model based on F1-Score
        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_model_name = name
            
    # Print Performance Table
    perf_df = pd.DataFrame(performance_records)
    print("\n", perf_df.to_string(index=False))
    
    # 6. Export the Best Performing Model and matching Vectorizer
    print(f"\n🏆 Best Model Selected: {best_model_name} (F1: {best_f1:.2f})")
    
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model, "models/best_model.joblib")
    joblib.dump(vectorizer, "models/tfidf_vectorizer.joblib")
    print("Saved model assets successfully inside 'models/' directory!")

if __name__ == "__main__":
    train_and_evaluate()