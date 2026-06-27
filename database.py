# database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgresss@localhost:5432/resume_screening_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class JobDescription(Base):
    __tablename__ = 'job_descriptions'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rankings = relationship("CandidateRanking", back_populates="job_description")

class Candidate(Base):
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resumes = relationship("Resume", back_populates="candidate", uselist=False)
    predictions = relationship("Prediction", back_populates="candidate", uselist=False)
    rankings = relationship("CandidateRanking", back_populates="candidate")

class Resume(Base):
    __tablename__ = 'resumes'
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id', ondelete='CASCADE'))
    file_path = Column(String(500), nullable=False)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=False)
    skills = Column(Text, nullable=True)  # Comma-separated list of extracted skills
    experience_years = Column(Float, default=0.0)
    education = Column(String(500), nullable=True)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id', ondelete='CASCADE'))
    model_name = Column(String(100), nullable=False)
    suitability_label = Column(String(50), nullable=False)  # "Suitable" or "Not Suitable"
    confidence_score = Column(Float, nullable=False)
    prediction_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="predictions")

class CandidateRanking(Base):
    __tablename__ = 'candidate_rankings'
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id', ondelete='CASCADE'))
    jd_id = Column(Integer, ForeignKey('job_descriptions.id', ondelete='CASCADE'))
    skill_match_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)  # Calculated score (e.g., 92.5%)
    status = Column(String(50), default="Pending") # Pending, Shortlisted, Rejected
    
    # Relationships
    candidate = relationship("Candidate", back_populates="rankings")
    job_description = relationship("JobDescription", back_populates="rankings")

def init_db():
    """Initializes and creates all tracking tables in PostgreSQL."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

def get_db():
    """Context manager generator for handling session lifecycles cleanely."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print("--- Testing Database Connection & Schema Deployment ---")
    init_db()