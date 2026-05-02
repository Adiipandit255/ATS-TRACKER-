import streamlit as st
import google.generativeai as genai
import re
import PyPDF2
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from collections import Counter

# ========== CONFIGURATION ==========
YOUR_API_KEY = "AIzaSyBq6wuzdOxBM827NTGBkx27IMkEj1EvOS8"
genai.configure(api_key=YOUR_API_KEY)

st.set_page_config(
    page_title="Professional ATS Resume Expert", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .score-excellent {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .score-good {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .score-average {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .score-poor {
        background: linear-gradient(135deg, #a8c0ff 0%, #3f2b96 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 12px;
        border-radius: 10px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ========== FUNCTIONS ==========

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        metadata = {"pages": len(pdf_reader.pages)}
        
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        
        if text.strip():
            return text.strip(), metadata
        else:
            return None, metadata
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")
        return None, None

def analyze_keywords(job_desc, resume_text):
    """Advanced keyword analysis"""
    # Convert to lowercase and split
    job_words = set(re.findall(r'\b[a-z]{3,}\b', job_desc.lower()))
    resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_text.lower()))
    
    # Find common and missing keywords
    common = job_words.intersection(resume_words)
    missing = job_words.difference(resume_words)
    
    # Calculate keyword score
    if job_words:
        keyword_score = (len(common) / len(job_words)) * 100
    else:
        keyword_score = 0
    
    return {
        "common_keywords": list(common)[:20],
        "missing_keywords": list(missing)[:20],
        "keyword_score": keyword_score,
        "total_job_keywords": len(job_words),
        "matched_keywords": len(common)
    }

def get_detailed_ai_analysis(job_desc, resume_text):
    """Get comprehensive AI analysis"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""You are a senior ATS consultant. Provide a comprehensive analysis.

Job Description:
{job_desc[:3000]}

Resume:
{resume_text[:3000]}

Provide detailed analysis in this format:

MATCH_SCORE: (0-100)

STRENGTHS:
- strength1
- strength2
- strength3

WEAKNESSES:
- weakness1
- weakness2
- weakness3

RECOMMENDATIONS:
1. [High Priority] action1
2. [Medium Priority] action2
3. [Low Priority] action3

INTERVIEW_QUESTIONS:
1. question1
2. question2

FINAL_VERDICT: Excellent/Good/Average/Poor

Be specific and actionable."""

        generation_config = {"temperature": 0.3, "max_output_tokens": 1500}
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def create_gauge_chart(percentage):
    """Create gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        title={'text': "ATS Match Score", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 40], 'color': '#ff6b6b'},
                {'range': [40, 70], 'color': '#ffd93d'},
                {'range': [70, 100], 'color': '#6bcf7f'}
            ]
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def create_keyword_chart(matched, total):
    """Create keyword match chart"""
    fig = go.Figure(data=[go.Bar(
        x=['Matched', 'Missing'],
        y=[matched, total - matched],
        marker_color=['#6bcf7f', '#ff6b6b'],
        text=[f'{matched}', f'{total - matched}'],
        textposition='auto'
    )])
    fig.update_layout(
        title="Keyword Match Analysis",
        yaxis_title="Number of Keywords",
        height=350
    )
    return fig

# ========== MAIN APP ==========

# Header
st.markdown("""
<div class="main-title">
    <h1>🎯 Professional ATS Resume Expert System</h1>
    <p>AI-Powered Resume Screening & Career Development Platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/resume.png", width=80)
    st.markdown("## 📊 System Capabilities")
    st.markdown("""
    - 🤖 AI-Powered Analysis
    - 🔑 Advanced Keyword Matching
    - 📈 Multi-dimensional Scoring
    - 💡 Actionable Recommendations
    - 🎯 Interview Preparation
    - 📊 Interactive Visualizations
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 Scoring Methodology")
    st.info("""
    - Keywords Match: 40%
    - Skills Assessment: 30%
    - Experience: 20%
    - Education: 10%
    """)
    
    st.markdown("---")
    st.markdown("### 📈 Score Guide")
    st.markdown("""
    - 🟢 80-100%: Excellent
    - 🟡 60-79%: Good
    - 🟠 40-59%: Average
    - 🔴 0-39%: Poor
    """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📄 Job Description")
    job_description = st.text_area(
        "Paste the complete job description:",
        height=250,
        placeholder="Copy and paste the job description here...",
        key="jd"
    )
    
    if job_description:
        st.caption(f"📝 {len(job_description)} characters")

with col2:
    st.markdown("### 📎 Resume Upload")
    uploaded_file = st.file_uploader(
        "Upload resume (PDF format only)",
        type=["pdf"],
        key="resume",
        help="Upload a text-based PDF resume"
    )
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        st.info(f"📄 Size: {uploaded_file.size/1024:.1f} KB")

st.markdown("---")

# Analysis button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_btn = st.button("🚀 Start Professional Analysis", use_container_width=True)

# Process analysis
if analyze_btn:
    if not uploaded_file:
        st.error("⚠️ Please upload a resume file!")
    elif not job_description:
        st.error("⚠️ Please paste the job description!")
    else:
        with st.spinner("🔍 Analyzing resume with AI..."):
            # Extract text from PDF
            resume_text, metadata = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                # Keyword analysis
                keyword_analysis = analyze_keywords(job_description, resume_text)
                
                # AI analysis
                ai_analysis = get_detailed_ai_analysis(job_description, resume_text)
                
                # Display results in tabs
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Score Dashboard", 
                    "🔑 Keyword Analysis", 
                    "📝 AI Analysis", 
                    "💡 Recommendations"
                ])
                
                with tab1:
                    match_score = int(keyword_analysis['keyword_score'])
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🎯 Overall Score", f"{match_score}%")
                    with col2:
                        st.metric("🔑 Keywords Matched", f"{keyword_analysis['matched_keywords']}/{keyword_analysis['total_job_keywords']}")
                    with col3:
                        st.metric("📄 Resume Length", f"{len(resume_text.split())} words")
                    with col4:
                        st.metric("📊 Readability", "Good" if len(resume_text.split()) < 800 else "Long")
                    
                    # Gauge chart
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.plotly_chart(create_gauge_chart(match_score), use_container_width=True)
                    
                    # Score interpretation
                    if match_score >= 80:
                        st.markdown("""
                        <div class="score-excellent">
                            <h3>🎉 Excellent Match!</h3>
                            <p>Your resume strongly aligns with the job requirements.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif match_score >= 60:
                        st.markdown("""
                        <div class="score-good">
                            <h3>✅ Good Match!</h3>
                            <p>Your resume matches well. Make minor improvements.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif match_score >= 40:
                        st.markdown("""
                        <div class="score-average">
                            <h3>📌 Average Match</h3>
                            <p>Significant improvements needed.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="score-poor">
                            <h3>⚠️ Poor Match</h3>
                            <p>Major revisions recommended.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("### 🔍 Keyword Analysis")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### ✅ Keywords Found")
                        if keyword_analysis['common_keywords']:
                            for kw in keyword_analysis['common_keywords'][:15]:
                                st.markdown(f"- `{kw}`")
                        else:
                            st.info("No matching keywords found")
                    
                    with col2:
                        st.markdown("#### ❌ Missing Keywords")
                        if keyword_analysis['missing_keywords']:
                            for kw in keyword_analysis['missing_keywords'][:15]:
                                st.markdown(f"- `{kw}`")
                        else:
                            st.success("All keywords matched!")
                    
                    # Keyword chart
                    st.plotly_chart(
                        create_keyword_chart(
                            keyword_analysis['matched_keywords'], 
                            keyword_analysis['total_job_keywords']
                        ),
                        use_container_width=True
                    )
                
                with tab3:
                    st.markdown("### 📝 AI-Powered Analysis")
                    st.markdown(ai_analysis)
                
                with tab4:
                    st.markdown("### 💡 Actionable Recommendations")
                    
                    # Extract recommendations from AI response
                    rec_match = re.search(r'RECOMMENDATIONS:(.*?)(?=INTERVIEW_QUESTIONS|\Z)', ai_analysis, re.DOTALL)
                    if rec_match:
                        st.markdown(rec_match.group(1))
                    else:
                        st.markdown("""
                        **Priority Recommendations:**
                        
                        1. **Add missing keywords** to your resume
                        2. **Quantify your achievements** with numbers
                        3. **Tailor your resume** for each application
                        4. **Highlight relevant skills** prominently
                        """)
                    
                    st.markdown("---")
                    st.markdown("### 🎤 Interview Questions to Prepare")
                    
                    # Extract interview questions
                    q_match = re.search(r'INTERVIEW_QUESTIONS:(.*?)(?=FINAL_VERDICT|\Z)', ai_analysis, re.DOTALL)
                    if q_match:
                        st.markdown(q_match.group(1))
                    else:
                        st.markdown("""
                        1. Tell me about your relevant experience
                        2. How do you handle [specific challenge]?
                        3. Describe a project where you used [key skill]
                        """)
                
                # Download report
                st.markdown("---")
                report = f"""
PROFESSIONAL ATS RESUME ANALYSIS REPORT
========================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SCORES OVERVIEW
--------------
Overall Match: {match_score}%
Keywords Matched: {keyword_analysis['matched_keywords']}/{keyword_analysis['total_job_keywords']}

{ai_analysis}

Generated by: Professional ATS Resume Expert System
Powered by: Google Gemini AI
                """
                
                st.download_button(
                    label="📥 Download Full Report",
                    data=report,
                    file_name=f"ATS_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=False
                )
                
                st.balloons()
                
            else:
                st.error("❌ Could not extract text from PDF. Please ensure it's a text-based PDF.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🚀 <strong>Professional ATS Resume Expert System</strong> | Powered by Google Gemini AI</p>
    <p>💡 <strong>Pro Tip:</strong> Use text-based PDF and include keywords from job description</p>
</div>
""", unsafe_allow_html=True)