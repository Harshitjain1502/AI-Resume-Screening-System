# preprocess.py
import re
import os
import PyPDF2
from docx import Document
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Initialize Lemmatizer and Stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def extract_text_from_pdf(file_path):
    """Extracts raw text from a PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extracts raw text from a DOCX file."""
    text = ""
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text

def extract_text(file_path):
    """Wrapper to handle multiple file extensions."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        return ""

def extract_contact_info(text):
    """Uses regular expressions to extract Email and Phone Numbers."""
    # Common email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else None

    # Flexible phone pattern supporting international and local formats
    phone_pattern = r'(?:(?:\+?\d{1,3}[-.\s\?]?)?\(?\d{3}\)?[-.\s\?]?\d{3}[-.\s\?]?\d{4}|\(\d{2}\)\s\d{4}-\d{4})'
    phones = re.findall(phone_pattern, text)
    phone = phones[0] if phones else None

    return {"email": email, "phone": phone}

def clean_and_normalize_text(text):
    """
    NLP Pipeline:
    1. Lowercasing & removal of non-alphabetic chars
    2. Tokenization
    3. Stopword Removal
    4. Lemmatization
    """
    if not text:
        return ""
    
    # Lowercase and replace non-letters with spaces
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Tokenize text
    tokens = word_tokenize(text)
    
    # Remove stopwords and lemmatize remaining tokens
    cleaned_tokens = [
        lemmatizer.lemmatize(token) 
        for token in tokens 
        if token not in stop_words and len(token) > 1
    ]
    
    # Re-join tokens into a cohesive clean string block
    return " ".join(cleaned_tokens)

if __name__ == "__main__":
    # Unit Test Block
    sample_text = """
    John Doe 
    Email: john.doe@example.com Phone: +1-555-0199
    Experienced Python Software Engineer specialized in Machine Learning and SQL.
    Building scalable data pipelines and deploying models to AWS.
    """
    print("--- Testing NLP Preprocessing Engine ---")
    contact = extract_contact_info(sample_text)
    cleaned = clean_and_normalize_text(sample_text)
    
    print(f"Extracted Contact: {contact}")
    print(f"Cleaned Text Output: {cleaned}")