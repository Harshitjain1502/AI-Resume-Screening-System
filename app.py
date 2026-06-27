# app.py
import streamlit as st
import pandas as pd
import time
from sqlalchemy import text
from database import SessionLocal, Candidate, Resume, JobDescription, CandidateRanking, Prediction
from preprocess import extract_text, extract_contact_info, clean_and_normalize_text
from ranking import calculate_match_score
import visualization as vis

# Page layout configuration setup
st.set_page_config(page_title="TalentPulse AI | Enterprise ATS", page_icon="🎯", layout="wide")

# Custom Dashboard Styling (Premium Deep Dark Cyber Theme)
st.markdown("""
    <style>
    /* Global Application Canvas */
    .stApp { 
        background: linear-gradient(145deg, #0b0e14 0%, #101520 100%) !important; 
        color: #e2e8f0 !important; 
    }
    
    /* Main Content text formatting */
    h1, h2, h3, h4, h5, h6, label, .stMarkdown { 
        color: #f8fafc !important; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Main Accent Title Glow */
    .main-title {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }

    /* Premium Component Panel Cards */
    .metric-card { 
        background: #151c2c; 
        padding: 24px; 
        border-radius: 12px; 
        border: 1px solid #24324f; 
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 15px;
    }
    .metric-card h5 { margin: 0 0 8px 0; color: #94a3b8 !important; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card h2 { margin: 0; font-size: 2.2rem; font-weight: 700; }

    /* Custom Input Element Overrides */
    .stTextArea textarea, .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: #111827 !important;
        color: #f3f4f6 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }
    
    /* Active Focus Glows */
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }

    /* Primary Action Buttons */
    .stButton>button { 
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important; 
        color: #ffffff !important; 
        font-weight: 600 !important;
        border-radius: 8px !important; 
        padding: 0.6rem 2rem !important; 
        border: none !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { 
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
    }
    
    /* Modern Navigation Tabs Customizing */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #111827;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #1f2937;
    }
    .stTabs [data-baseweb="tab"] {
        color: #9ca3af !important;
        border-radius: 6px !important;
        padding: 8px 20px !important;
        background-color: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f2937 !important;
        color: #38bdf8 !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Access System
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<p class="main-title">🔒 TalentPulse AI Portal</p>', unsafe_allow_html=True)
    st.markdown("Please verify credentials to synchronize local cluster workspace.")
    st.markdown("---")
    
    col_login, _ = st.columns([1, 2])
    with col_login:
        username = st.text_input("Username Identifier")
        password = st.text_input("Security Access Token", type="password")
        if st.button("Unlock Core Systems"):
            if username == "admin" and password == "recruiter2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Authentication check failed. Access Denied.")
    st.stop()

# Initialize Database Local Pipeline Session 
db = SessionLocal()

# Global Platform Header
col_logo, col_logout = st.columns([8, 1])
with col_logo:
    st.markdown('<p class="main-title">🎯 TalentPulse AI</p>', unsafe_allow_html=True)
    st.caption("Next-Gen Vector Screening & Talent Intelligence Analytics Network")
with col_logout:
    if st.button("Sign Out"):
        st.session_state.authenticated = False
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Navigation Viewport Frame Tabs Configuration
tab_dash, tab_screen, tab_db = st.tabs(["📊 Analytics Suite", "📥 Pipeline Ingestion Engine", "🔍 Candidate Repository"])

# ----------------------------------------------------
# TAB 1: ENTERPRISE ANALYTICS OVERVIEW
# ----------------------------------------------------
with tab_dash:
    total_candidates = db.query(Candidate).count()
    shortlisted = db.query(CandidateRanking).filter(CandidateRanking.final_score >= 75.0).count()
    rejected = max(0, total_candidates - shortlisted)
    
    # Structural Dashboard Panel Cards Grid
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h5>Active Ingest Volume</h5><h2>{total_candidates} Resumes</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h5>AI Shortlisted (≥75%)</h5><h2 style="color:#4ade80;">{shortlisted} Profiles</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h5>Flagged / Low Fit</h5><h2 style="color:#f87171;">{rejected} Profiles</h2></div>', unsafe_allow_html=True)
        
    st.markdown("<br>### 📈 Data Distribution & ML Vector Verification Matrices", unsafe_allow_html=True)
    col4, col5 = st.columns([1, 1])
    with col4:
        if total_candidates > 0:
            st.pyplot(vis.generate_pie_chart(["Shortlisted", "Low Fit"], [shortlisted, rejected]))
        else:
            st.info("Pipeline telemetry index empty. Process applicant assets to generate visualizations.")
    with col5:
        st.pyplot(vis.generate_confusion_matrix_plot())

# ----------------------------------------------------
# TAB 2: INTERACTIVE BATCH INGESTION SCREENER
# ----------------------------------------------------
with tab_screen:
    st.markdown("### 📥 Create Targeted Requisition Screening Filter")
    st.markdown("Setup extraction metrics against raw text documents automatically.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_jd, col_upload = st.columns([1, 1])
    
    with col_jd:
        st.markdown("**1. Target Job Criteria Metrics**")
        jd_input = st.text_area(
            "Configure Mandatory Target Parameters & Core Technologies Stack:",
            "Python Machine Learning SQL Docker AWS Cloud Engineer Data Science pipelines Devops Kubernetes",
            height=200
        )
    with col_upload:
        st.markdown("**2. Binary Application Attachment Workspace**")
        uploaded_files = st.file_uploader("Drop candidate profile records here (.pdf, .docx):", type=["pdf", "docx"], accept_multiple_files=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Trigger Quantum Matching Pipeline") and uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        jd_record = JobDescription(title="Requisition Verification Filter", raw_text=jd_input, cleaned_text=clean_and_normalize_text(jd_input))
        db.add(jd_record)
        db.commit()
        
        for index, file in enumerate(uploaded_files):
            status_text.text(f"Parsing structural properties from: {file.name}")
            
            temp_path = f"uploads/{file.name}"
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
                
            raw_txt = extract_text(temp_path)
            cleaned_txt = clean_and_normalize_text(raw_txt)
            contact = extract_contact_info(raw_txt)
            
            cand_name = file.name.split('.')[0].replace('_', ' ').title()
            parsed_email = contact['email'] if contact['email'] else f"unknown_{file.name}@example.com"
            
            candidate_record = db.query(Candidate).filter(Candidate.email == parsed_email).first()
            if not candidate_record:
                candidate_record = Candidate(name=cand_name, email=parsed_email, phone=contact['phone'])
                db.add(candidate_record)
                db.commit()
            
            final_percentage_score = calculate_match_score(raw_txt, jd_input)
            
            resume_record = Resume(candidate_id=candidate_record.id, file_path=temp_path, raw_text=raw_txt, cleaned_text=cleaned_txt)
            db.add(resume_record)
            
            suitability = "Suitable" if final_percentage_score >= 70.0 else "Not Suitable"
            pred_record = Prediction(candidate_id=candidate_record.id, model_name="Logistic Regression Pipeline", suitability_label=suitability, confidence_score=final_percentage_score/100.0)
            db.add(pred_record)
            
            rank_record = CandidateRanking(candidate_id=candidate_record.id, jd_id=jd_record.id, skill_match_score=final_percentage_score, final_score=final_percentage_score, status="Shortlisted" if suitability == "Suitable" else "Rejected")
            db.add(rank_record)
            db.commit()
            
            progress_bar.progress((index + 1) / len(uploaded_files))
            time.sleep(0.15)
            
        status_text.empty()
        st.success(f"Successfully vectorized and parsed all {len(uploaded_files)} portfolios inside PostgreSQL cluster layers!")

# ----------------------------------------------------
# TAB 3: CANDIDATE REPOSITORY & ADVANCED FILTER SEARCH
# ----------------------------------------------------
with tab_db:
    st.markdown("### 🔍 Integrated Pipeline Index Ledger")
    
    query = """
        SELECT c.id AS "ID", c.name AS "Candidate Name", c.email AS "Email Handle", 
               r.final_score AS "Match Score (%)", r.status AS "Pipeline Status" 
        FROM candidates c 
        JOIN candidate_rankings r ON c.id = r.candidate_id 
        ORDER BY r.final_score DESC
    """
    
    # Safe executed SQLAlchemy textual binding format
    with db.bind.connect() as connection:
        df_candidates = pd.read_sql(text(query), connection)
    
    if not df_candidates.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search_query = st.text_input("🔍 Filter Ledger Profiles by Name / Contact Handle:")
        with col_f2:
            status_filter = st.selectbox("Workflow Operational Status Classification:", ["All Candidates", "Shortlisted", "Rejected"])
            
        filtered_df = df_candidates.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["Candidate Name"].str.contains(search_query, case=False) | 
                filtered_df["Email Handle"].str.contains(search_query, case=False)
            ]
        if status_filter != "All Candidates":
            filtered_df = filtered_df[filtered_df["Pipeline Status"] == status_filter]
            
        # Display the custom colored dataframe grid matrix
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("📥 Export Current Filter Context to CSV", data=csv_data, file_name="filtered_pipeline_report.csv", mime="text/csv")
    else:
        st.info("No records indexed inside database cluster layers. Upload resumes to construct entries.")

db.close()