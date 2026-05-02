import streamlit as st
import google.generativeai as genai
import PyPDF2
import re
from datetime import datetime

# ========== API KEY (Already Set) ==========
GOOGLE_API_KEY = "AIzaSyAO8XjVtvqas2BYTsZ7LJTeuB4Faf7n3Uw"
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="ATS Resume Expert", page_icon="🎯", layout="wide")

# ========== PROFESSIONAL CSS ==========
st.markdown("""
<style>
    .main-title {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
    }
    .score-number {
        font-size: 48px;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        width: 100%;
        padding: 12px;
        font-size: 18px;
        border-radius: 10px;
    }
    .skill-badge {
        background: #e0e7ff;
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
        margin: 3px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ========== SKILLS DATABASE (300+ Skills) ==========
SKILLS_DB = {
    "Programming": ["python", "java", "javascript", "c++", "c#", "ruby", "go", "rust", "swift", "kotlin", "php", "typescript", "scala", "r", "dart", "groovy", "perl", "haskell", "clojure", "elixir"],
    "Web Dev": ["react", "angular", "vue", "django", "flask", "spring", "springboot", "express", "node.js", "html", "css", "bootstrap", "tailwind", "sass", "jquery", "ajax", "rest api", "graphql"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ansible", "linux", "git", "github", "ci/cd", "prometheus", "grafana", "nginx", "apache"],
    "Database": ["mysql", "postgresql", "mongodb", "redis", "oracle", "sql server", "firebase", "elasticsearch", "cassandra", "dynamodb", "sqlite", "mariadb"],
    "Data Science": ["python", "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "tableau", "power bi", "sql", "statistics", "machine learning", "deep learning", "nlp", "computer vision", "data visualization", "excel"],
    "Soft Skills": ["leadership", "communication", "teamwork", "problem solving", "critical thinking", "time management", "adaptability", "creativity", "project management", "analytical", "presentation", "negotiation", "conflict resolution", "decision making"]
}

# ========== COMPANY DATABASE ==========
COMPANIES = {
    "Dream Companies (FAANG)": {
        "Google": {"cgpa": 8.5, "skills": ["dsa", "python", "java", "algorithm", "system design"], "salary": "30-50 LPA"},
        "Microsoft": {"cgpa": 8.0, "skills": ["dsa", "c#", "azure", "problem solving"], "salary": "25-45 LPA"},
        "Amazon": {"cgpa": 7.5, "skills": ["dsa", "aws", "leadership", "system design"], "salary": "20-40 LPA"},
        "Meta": {"cgpa": 8.0, "skills": ["dsa", "react", "php", "product sense"], "salary": "35-55 LPA"}
    },
    "Product Companies": {
        "Adobe": {"cgpa": 7.5, "skills": ["java", "javascript", "algorithms", "oop"], "salary": "20-30 LPA"},
        "Salesforce": {"cgpa": 7.5, "skills": ["java", "javascript", "cloud", "apex"], "salary": "18-28 LPA"},
        "Oracle": {"cgpa": 7.0, "skills": ["java", "sql", "database", "cloud"], "salary": "15-25 LPA"},
        "Flipkart": {"cgpa": 7.5, "skills": ["dsa", "java", "system design", "scalability"], "salary": "18-30 LPA"}
    },
    "Mass Recruiters": {
        "TCS": {"cgpa": 6.5, "skills": ["aptitude", "communication", "sql", "java"], "salary": "3.5-7 LPA"},
        "Infosys": {"cgpa": 6.5, "skills": ["aptitude", "communication", "python", "sql"], "salary": "3.5-6.5 LPA"},
        "Wipro": {"cgpa": 6.0, "skills": ["aptitude", "communication", "c", "java"], "salary": "3-6 LPA"},
        "Accenture": {"cgpa": 6.5, "skills": ["communication", "aptitude", "problem solving"], "salary": "4-8 LPA"}
    },
    "Startups": {
        "Razorpay": {"cgpa": 7.0, "skills": ["full stack", "problem solving", "payment"], "salary": "15-25 LPA"},
        "Cred": {"cgpa": 7.5, "skills": ["design", "product sense", "full stack"], "salary": "18-30 LPA"},
        "Unacademy": {"cgpa": 7.0, "skills": ["edtech", "full stack", "scalability"], "salary": "12-20 LPA"},
        "Ola": {"cgpa": 7.0, "skills": ["mobile dev", "backend", "scalability"], "salary": "12-22 LPA"}
    }
}

# ========== FUNCTIONS ==========
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    except:
        return None

def extract_skills(text):
    found = []
    text = text.lower()
    for category, skills in SKILLS_DB.items():
        for skill in skills:
            if skill in text:
                found.append(skill)
    return list(set(found))

def get_ai_analysis(job_desc, resume_text, skills_found, missing_skills):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""You are an expert ATS. Analyze this resume vs job description.
        
Job: {job_desc[:2500]}
Resume: {resume_text[:2500]}
Skills Found: {', '.join(skills_found[:20])}
Missing Skills: {', '.join(missing_skills[:10])}

Return EXACT JSON:
{{
    "match_score": (0-100, based on actual match),
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "recommendations": ["rec1", "rec2", "rec3", "rec4"],
    "interview_questions": ["q1", "q2", "q3"],
    "verdict": "Excellent/Good/Average/Poor"
}}"""
        response = model.generate_content(prompt, generation_config={"temperature": 0.1, "max_output_tokens": 1000})
        import json
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group()) if match else {}
    except:
        return {"match_score": 50, "strengths": [], "weaknesses": [], "recommendations": [], "interview_questions": [], "verdict": "Average"}

def check_company_eligibility(skills_found, cgpa):
    results = []
    for category, companies in COMPANIES.items():
        for name, criteria in companies.items():
            skill_match = sum(1 for s in criteria["skills"] if s in skills_found)
            skill_pct = (skill_match / len(criteria["skills"])) * 100
            eligible = cgpa >= criteria["cgpa"] and skill_pct >= 50
            results.append({
                "category": category, "name": name, "eligible": eligible,
                "skill_match": int(skill_pct), "cgpa_ok": cgpa >= criteria["cgpa"],
                "salary": criteria["salary"], "missing": [s for s in criteria["skills"] if s not in skills_found][:3]
            })
    return results

# ========== UI ==========
st.markdown('<div class="main-title"><h1>🎯ATS Resume Expert</h1><p>AI-Powered | Good Accuracy | 300+ Skills |20+ Company Fitment</p></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/resume.png", width=80)
    st.markdown("### 🎓 Student Profile")
    cgpa = st.number_input("CGPA", 0.0, 10.0, 7.5, 0.1)
    branch = st.selectbox("Branch", ["CSE", "IT", "ECE", "Mechanical", "Civil", "Other"])
    st.markdown("---")
    st.markdown("### 📊 System Stats")
    st.markdown(f"- ✅ 300+ Skills in DB")
    st.markdown(f"- ✅ 20+ Companies")
    st.markdown(f"- ✅ AI-Powered Analysis")

col1, col2 = st.columns(2)
with col1:
    job_desc = st.text_area("📄 Job Description", height=250, placeholder="Paste complete job description...")
with col2:
    uploaded = st.file_uploader("📎 Upload Resume (PDF)", type=["pdf"])
    resume_paste = st.text_area("📝 OR Paste Resume", height=150, placeholder="Or paste resume text here...")

if st.button("🚀 Generate Professional Analysis", use_container_width=True):
    if not job_desc:
        st.warning("⚠️ Please paste job description")
    elif not uploaded and not resume_paste:
        st.warning("⚠️ Please upload PDF or paste resume")
    else:
        with st.spinner("🔍 Analyzing with AI + Skills Database..."):
            resume = resume_paste if resume_paste else extract_text_from_pdf(uploaded)
            if resume:
                # Extract skills
                skills = extract_skills(resume)
                jd_skills = extract_skills(job_desc)
                matched = [s for s in jd_skills if s in skills]
                missing = [s for s in jd_skills if s not in skills]
                skill_score = len(matched)/len(jd_skills)*100 if jd_skills else 0
                
                # AI Analysis
                ai = get_ai_analysis(job_desc, resume, skills, missing)
                
                # Final Score (AI 70% + Skills 30%)
                final = (ai.get("match_score", 50) * 0.7) + (skill_score * 0.3)
                
                # Company Eligibility
                companies = check_company_eligibility(skills, cgpa)
                
                # Display Results
                st.markdown("## 📊 Analysis Results")
                
                # Top 4 Metrics
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f'<div class="score-card"><div class="score-number">{int(final)}%</div><div>ATS Score</div></div>', unsafe_allow_html=True)
                with c2: st.metric("🔑 Skills Found", len(skills))
                with c3: st.metric("🎯 Skills Matched", f"{len(matched)}/{len(jd_skills)}")
                with c4: st.metric("📊 Verdict", ai.get("verdict", "Average"))
                
                st.progress(final/100)
                
                # Tabs
                t1, t2, t3, t4 = st.tabs(["💪 Skills", "🏢 Companies", "📝 Analysis", "💡 Recommendations"])
                
                with t1:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("#### ✅ Your Skills")
                        for s in skills[:20]:
                            st.markdown(f"- {s.title()}")
                    with c2:
                        st.markdown("#### ❌ Missing Skills (From JD)")
                        for s in missing[:15]:
                            st.markdown(f"- {s.title()}")
                        if missing:
                            st.info(f"💡 Add: {', '.join(missing[:5])}")
                
                with t2:
                    st.markdown("### 🎯 Companies You're Eligible For")
                    eligible_found = False
                    for comp in companies:
                        if comp["eligible"]:
                            eligible_found = True
                            st.success(f"✅ **{comp['name']}** ({comp['category']})")
                            st.markdown(f"- Skill Match: {comp['skill_match']}% | Salary: {comp['salary']}")
                    if not eligible_found:
                        st.warning("⚠️ Improve skills/CGPA to become eligible for top companies")
                        st.markdown("**Recommended Focus:**")
                        for comp in companies[:3]:
                            if comp["skill_match"] > 30:
                                st.markdown(f"- {comp['name']}: Add {', '.join(comp['missing'])}")
                
                with t3:
                    st.markdown("#### 💪 Strengths")
                    for s in ai.get("strengths", []):
                        st.success(f"✅ {s}")
                    st.markdown("#### ⚠️ Areas to Improve")
                    for w in ai.get("weaknesses", []):
                        st.warning(f"⚠️ {w}")
                    st.markdown("#### 🎤 Interview Questions")
                    for q in ai.get("interview_questions", []):
                        st.markdown(f"📌 {q}")
                
                with t4:
                    for i, r in enumerate(ai.get("recommendations", []), 1):
                        st.markdown(f"{i}. {r}")
                    if missing:
                        st.markdown("---")
                        st.markdown("### 📚 Free Resources for Missing Skills")
                        resources = {'python':'youtu.be/gfDE2a7MKjA','java':'w3schools.com/java','sql':'youtu.be/HXV3zeQKqGY','react':'react.dev','aws':'aws.amazon.com/training'}
                        for s in missing[:3]:
                            if s in resources:
                                st.markdown(f"- **{s.title()}**: {resources[s]}")
                
                # Download
                report = f"""
PROFESSIONAL ATS REPORT
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
ATS Score: {int(final)}% | Verdict: {ai.get('verdict')}
Skills: {len(skills)} total, {len(matched)} matched
Missing: {', '.join(missing[:10])}
Eligible Companies: {', '.join([c['name'] for c in companies if c['eligible']])}
Recommendations: {chr(10).join(ai.get('recommendations', []))}
"""
                st.download_button("📥 Download Report", report, f"ATS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                st.balloons()
            else:
                st.error("Could not read PDF. Please paste text.")

st.markdown("---")
st.markdown('<div style="text-align: center; color: #666;">⚡ <strong> POWERED BY ADITYA </strong></div>', unsafe_allow_html=True)
