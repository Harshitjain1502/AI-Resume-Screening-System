# ranking.py
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import clean_and_normalize_text

def calculate_match_score(resume_text, jd_text):
    """
    Calculates a dynamic candidate score based on:
    1. NLP Skill Match Score via Cosine Similarity (60% weight)
    2. ML Model Suitability Assessment (40% weight)
    """
    try:
        # Load saved ML pipelines
        vectorizer = joblib.load("models/tfidf_vectorizer.joblib")
        model = joblib.load("models/best_model.joblib")
    except FileNotFoundError:
        print("Error: Model assets not found! Please run train_model.py first.")
        return 0.0

    # Step 1: Preprocess and clean text streams
    cleaned_resume = clean_and_normalize_text(resume_text)
    cleaned_jd = clean_and_normalize_text(jd_text)

    if not cleaned_resume or not cleaned_jd:
        return 0.0

    # Step 2: Calculate Semantic Skill Match Score using Cosine Similarity
    # Transform both strings using the exact same vectorizer vocabulary
    vectors = vectorizer.transform([cleaned_resume, cleaned_jd])
    similarity_matrix = cosine_similarity(vectors[0:1], vectors[1:2])
    skill_match_score = float(similarity_matrix[0][0]) # Ranges from 0.0 to 1.0

    # Step 3: Extract ML Prediction Probabilities
    # Check probability of candidate being class '1' (Suitable)
    resume_vector = vectorizer.transform([cleaned_resume])
    
    if hasattr(model, "predict_proba"):
        ml_probability = float(model.predict_proba(resume_vector)[0][1])
    else:
        # Fallback if model doesn't support probabilities
        ml_probability = float(model.predict(resume_vector)[0])

    # Step 4: Compute Weighted Aggregate Final Score
    # 60% assigned to text match alignment, 40% to structural machine prediction
    final_score = (skill_match_score * 0.6) + (ml_probability * 0.4)
    
    # Format as a clean percentage score out of 100
    final_percentage = round(final_score * 100, 2)
    return min(final_percentage, 100.0)

if __name__ == "__main__":
    print("--- Testing Candidate Ranking Engine ---")
    
    # Mock inputs for checking calculations
    sample_resume = "Experienced python developer skilled in machine learning, data science, and sql."
    sample_jd = "Looking for a python machine learning engineer with robust knowledge of SQL databases."
    
    score = calculate_match_score(sample_resume, sample_jd)
    print(f"Calculated Candidate Match Score: {score}%")