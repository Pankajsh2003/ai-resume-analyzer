# app.py (AI Resume Analyzer  Deploy Version)
import streamlit as st
import json
import re
import nltk
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from utils.resume_parser import extract_text_from_pdf

nltk.download('punkt', quiet=True)

# -----------------------------
# Config + example keyword data
# -----------------------------
st.set_page_config(page_title="AI Resume Analyzer ", page_icon="🧠", layout="wide")

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
    }
}

# -----------------------------
# Styles
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b1020, #102240);
        color: #e6f7ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .card {
        background: rgba(255,255,255,0.04);
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 6px 20px rgba(3,12,36,0.6);
        margin-bottom: 14px;
    }
    h1 { color:#7ef0ff !important; text-align:center; text-shadow:0 2px 10px rgba(0,0,0,0.6);}
    .small-muted { color:#bcd; font-size:13px; }
    .skill-pill {
        display:inline-block;
        padding:6px 10px;
        margin:4px;
        border-radius:999px;
        background:rgba(255,255,255,0.06);
    }
    pre {
        white-space: pre-wrap;
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 8px;
        color: #dff6ff;
        font-size: 13px;
        max-height: 300px;
        overflow-y: auto;
    }
    footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.title("🧠 AI Resume Analyzer ")
st.markdown("<p class='small-muted' style='text-align:center;'>Deep skill analysis • structured insights • smart suggestions • PDF report</p>", unsafe_allow_html=True)
st.markdown("---")

# -----------------------------
# Inputs
# -----------------------------
col_left, col_right = st.columns([2, 1])
with col_left:
    uploaded_file = st.file_uploader("📂 Upload your resume (PDF)", type=["pdf"])
with col_right:
    job_role = st.selectbox("🎯 Target Job Role", list(job_keywords.keys()))
    show_details = st.checkbox("Show raw extracted text (organized view)", value=False)

# -----------------------------
# Helpers
# -----------------------------
def normalize_text(t: str) -> str:
    return re.sub(r'\s+', ' ', t).lower()

def analyze_categorized(resume_text: str, role_key: str):
    role_map = job_keywords.get(role_key, {})
    found = {"Technical": [], "Tools": []}
    missing = {"Technical": [], "Tools": []}

    for cat, kws in role_map.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', resume_text):
                found[cat].append(kw)
            else:
                missing[cat].append(kw)
    total_checked = sum(len(kws) for kws in role_map.values())
    total_found = sum(len(v) for v in found.values())
    score = int((total_found / total_checked) * 100) if total_checked > 0 else 0
    return score, found, missing

def create_pdf_bytes(role, score, found, missing, resume_snippet):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, f"AI Resume Analysis Report - {role}", ln=True, align='C')
    pdf.ln(6)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 6, f"Job Readiness Score: {score}/100", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Skills Found:", ln=True)
    pdf.set_font("Arial", size=11)
    for cat, items in found.items():
        pdf.cell(0, 6, f"  {cat}: " + (", ".join(items) if items else "None"), ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Missing Skills:", ln=True)
    pdf.set_font("Arial", size=11)
    for cat, items in missing.items():
        pdf.cell(0, 6, f"  {cat}: " + (", ".join(items) if items else "None"), ln=True)
    pdf.ln(6)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Resume Snippet (first 400 chars):", ln=True)
    pdf.set_font("Arial", size=10)
    snippet = resume_snippet.replace('\n', ' ')[:400]
    pdf.multi_cell(0, 6, snippet)
    pdf.ln(8)

    pdf.set_font("Arial", size=9)
    pdf.multi_cell(0, 6, "Notes: Automated keyword analysis. Use the missing skills to enhance your resume.")
    raw = pdf.output(dest='S').encode('latin-1')
    return raw

# -----------------------------
# Main Logic
# -----------------------------
if uploaded_file and job_role:
    resume_text_raw = extract_text_from_pdf(uploaded_file)
    resume_text = normalize_text(resume_text_raw)

    if show_details:
        st.markdown("<div class='card'><b>📜 Extracted & Organized Text (Preview):</b></div>", unsafe_allow_html=True)
        clean_blocks = resume_text_raw.split('\n')
        formatted_preview = "\n".join([f"• {line.strip()}" for line in clean_blocks if line.strip()])[:1200]
        st.markdown(f"<pre>{formatted_preview}</pre>", unsafe_allow_html=True)

    with st.spinner("⚙️ Running smart analysis..."):
        score, found, missing = analyze_categorized(resume_text, job_role)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### 📊 Job Readiness Score — <span style='color:#7ef0ff;'>{score}/100</span>", unsafe_allow_html=True)
    st.progress(score / 100)
    st.markdown("</div>", unsafe_allow_html=True)

    # Smart summary
    summary_line = f"Your resume matches {score}% of {job_role} skills."
    if score < 60:
        summary_line += " You should focus on learning key missing skills and updating your project descriptions."
    elif score < 85:
        summary_line += " Good job! A few missing tools or technologies can make it stronger."
    else:
        summary_line += " Excellent! Your resume is nearly perfect for this role."
    st.success(summary_line)

    # 3-column Insights
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown("<div class='card'><h4>💪 Strengths</h4>", unsafe_allow_html=True)
        top_found = [it for cat in found.values() for it in cat][:5]
        if top_found:
            for s in top_found:
                st.markdown(f"<span class='skill-pill'>{s}</span>", unsafe_allow_html=True)
        else:
            st.write("No clear strengths found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='card'><h4>⚠️ Missing Skills</h4>", unsafe_allow_html=True)
        top_missing = [it for cat in missing.values() for it in cat][:6]
        if top_missing:
            for s in top_missing:
                st.markdown(f"<span class='skill-pill'>{s}</span>", unsafe_allow_html=True)
        else:
            st.write("All good here.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='card'><h4>💡 Suggestions</h4>", unsafe_allow_html=True)
        suggestions = []
        if "python" in [k.lower() for k in sum(found.values(), [])]:
            suggestions.append("Add project bullet points showing Python-based achievements.")
        if len(sum(missing.values(), [])) > 0:
            suggestions.append("Mention missing keywords in skill or project sections.")
        if not found:
            suggestions.append("Include measurable project outcomes and tools used.")
        for s in suggestions[:4]:
            st.markdown(f"- {s}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Visualizations (half size)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📈 Skill Coverage Visualization")

    matched = sum(len(v) for v in found.values())
    total = matched + sum(len(v) for v in missing.values())
    sizes = [matched, total - matched] if total > 0 else [0, 1]
    labels = ['Matched', 'Missing']
    fig1, ax1 = plt.subplots(figsize=(3, 3))
    ax1.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90, colors=['#7ef0ff', '#3b82f6'])
    ax1.axis('equal')
    st.pyplot(fig1)

    cats = list(found.keys())
    matched_counts = [len(found[c]) for c in cats]
    missing_counts = [len(missing[c]) for c in cats]
    x = range(len(cats))
    fig2, ax2 = plt.subplots(figsize=(4, 2))
    ax2.bar(x, matched_counts, width=0.4, label='Matched', color='#7ef0ff')
    ax2.bar([i + 0.4 for i in x], missing_counts, width=0.4, label='Missing', color='#60a5fa')
    ax2.set_xticks([i + 0.2 for i in x])
    ax2.set_xticklabels(cats)
    ax2.set_ylabel('Count')
    ax2.legend()
    st.pyplot(fig2)
    st.markdown("</div>", unsafe_allow_html=True)

    # PDF Download
    resume_snip = resume_text_raw[:500]
    pdf_bytes = create_pdf_bytes(job_role, score, found, missing, resume_snip)
    st.download_button("📥 Download Detailed Report (PDF)", data=pdf_bytes, file_name="Resume_Analysis_Report.pdf", mime="application/pdf")

else:
    st.info("Upload a resume (PDF) and choose a role to start analysis.")
