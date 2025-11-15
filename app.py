# app.py (AI Resume Analyzer – Clean & Visible Version)
import streamlit as st
import json
import re
import nltk
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from utils.resume_parser import extract_text_from_pdf

nltk.download('punkt', quiet=True)

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="🧠", layout="wide")

job_keywords = {
    "Data Analyst": {
        "Technical": ["python", "pandas", "numpy", "statistics", "machine learning"],
        "Tools": ["excel", "power bi", "tableau", "sql"]
    },
    "Web Developer": {
        "Technical": ["html", "css", "javascript", "react", "node.js"],
        "Tools": ["git", "webpack", "npm", "rest api", "mongodb"]
    },
    "AI Engineer": {
        "Technical": ["python", "tensorflow", "pytorch", "deep learning", "nlp"],
        "Tools": ["numpy", "pandas", "scikit-learn", "docker"]
    },

    # ⭐ NEW ROLE ADDED ⭐
    "Software Developer": {
        "Technical": ["python", "java", "c++", "oops", "data structures", "algorithms"],
        "Tools": ["git", "github", "docker", "linux", "rest api"]
    }
}


# ---------------------------------------------------
# GLOBAL THEME FIXED (more visible colors)
# ---------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: #0d1117;
        color: #c9d1d9;
        font-family: 'Segoe UI';
    }
    .card {
        background: #161b22;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
        margin-bottom: 15px;
    }
    h1, h2, h3, h4 { color: #58a6ff !important; }
    .skill-pill {
        display:inline-block;
        padding:6px 12px;
        background:#21262d;
        border-radius:50px;
        margin:4px;
        color:#9ecbff;
        border:1px solid #30363d;
    }
    pre {
        background:#161b22;
        color:#c9d1d9;
        padding:15px;
        border-radius:8px;
        max-height:300px;
        overflow-y:auto;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("🧠 AI Resume Analyzer")
st.markdown("<p style='text-align:center; color:#8b949e;'>AI-powered skill detection • Missing skills • PDF report</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------
# INPUTS
# ---------------------------------------------------
left, right = st.columns([2, 1])

with left:
    uploaded_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])

with right:
    job_role = st.selectbox("🎯 Select Target Job Role", list(job_keywords.keys()))
    show_details = st.checkbox("Show Extracted Text", value=False)

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
def normalize(t):
    return re.sub(r"\s+", " ", t).lower()

def analyze(resume, role):
    rm = job_keywords.get(role, {})
    found, missing = {"Technical": [], "Tools": []}, {"Technical": [], "Tools": []}

    for cat, kws in rm.items():
        for kw in kws:
            if re.search(rf"\\b{re.escape(kw.lower())}\\b", resume):
                found[cat].append(kw)
            else:
                missing[cat].append(kw)

    total = sum(len(v) for v in rm.values())
    matches = sum(len(v) for v in found.values())
    score = int((matches / total) * 100) if total else 0
    return score, found, missing

def create_pdf(role, score, found, missing, snippet):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, f"AI Resume Report — {role}", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"Score: {score}/100", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Skills Found:", ln=True)
    pdf.set_font("Arial", "", 11)
    for c, x in found.items():
        pdf.cell(0, 6, f"{c}: {', '.join(x) if x else 'None'}", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Missing Skills:", ln=True)
    pdf.set_font("Arial", "", 11)
    for c, x in missing.items():
        pdf.cell(0, 6, f"{c}: {', '.join(x) if x else 'None'}", ln=True)

    pdf.ln(6)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Resume Snippet:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, snippet[:450])

    return pdf.output(dest="S").encode("latin-1")

# ---------------------------------------------------
# MAIN LOGIC
# ---------------------------------------------------
if uploaded_file and job_role:
    text_raw = extract_text_from_pdf(uploaded_file)
    text = normalize(text_raw)

    if show_details:
        st.markdown("<div class='card'><b>📜 Extracted Text:</b></div>", unsafe_allow_html=True)
        st.markdown(f"<pre>{text_raw[:1500]}</pre>", unsafe_allow_html=True)

    with st.spinner("Analyzing skills..."):
        score, found, missing = analyze(text, job_role)

    # SCORE CARD
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader(f"📊 Job Readiness Score: {score}/100")
    st.progress(score / 100)
    st.markdown("</div>", unsafe_allow_html=True)

    # SUMMARY
    if score < 60:
        st.error("Your resume needs improvement. Missing many required skills.")
    elif score < 85:
        st.warning("Good resume! But you can add more technical tools.")
    else:
        st.success("Excellent resume! Strong match for this job role.")

    # INSIGHTS 3-COLUMN
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='card'><h4>💪 Strengths</h4>", unsafe_allow_html=True)
        for s in sum(found.values(), [])[:6]:
            st.markdown(f"<span class='skill-pill'>{s}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'><h4>⚠️ Missing Skills</h4>", unsafe_allow_html=True)
        for s in sum(missing.values(), [])[:6]:
            st.markdown(f"<span class='skill-pill'>{s}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='card'><h4>💡 Suggestions</h4>", unsafe_allow_html=True)
        st.markdown("- Add missing skills in the Skills section.")
        st.markdown("- Include project details mentioning tools used.")
        st.markdown("- Add quantifiable achievements.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------
    # CHARTS (fixed – no manual colors)
    # ---------------------------------------------------

    st.subheader("📈 Skill Visualization")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    matched = sum(len(v) for v in found.values())
    total = matched + sum(len(v) for v in missing.values())

    # PIE CHART (auto colors)
    fig1, ax1 = plt.subplots(figsize=(3, 3))
    ax1.pie(
        [matched, total - matched],
        labels=["Matched", "Missing"],
        autopct="%1.0f%%",
        startangle=90
    )
    ax1.axis("equal")
    st.pyplot(fig1)

    # BAR CHART (auto colors)
    cats = list(found.keys())
    fcounts = [len(found[c]) for c in cats]
    mcounts = [len(missing[c]) for c in cats]

    fig2, ax2 = plt.subplots(figsize=(4, 3))
    x = range(len(cats))
    ax2.bar(x, fcounts, width=0.4, label="Matched")
    ax2.bar([i + 0.4 for i in x], mcounts, width=0.4, label="Missing")
    ax2.set_xticks([i + 0.2 for i in x])
    ax2.set_xticklabels(cats)
    ax2.set_ylabel("Count")
    ax2.legend()
    st.pyplot(fig2)

    st.markdown("</div>", unsafe_allow_html=True)

    # DOWNLOAD PDF
    pdf_bytes = create_pdf(job_role, score, found, missing, text_raw)
    st.download_button(
        "📥 Download PDF Report",
        data=pdf_bytes,
        file_name="Resume_Report.pdf",
        mime="application/pdf"
    )

else:
    st.info("Upload a PDF resume to start analysis.")
