import streamlit as st
from utils.file_reader import extract_text_and_links
from utils.web_scraper import scrape_links
from utils.ranker import rank_resumes
import openai
import time
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# GPT-3.5 Ranking Function (for OpenAI >=1.0.0)
def gpt_rank_resume(job_desc, resume_text, api_key):
    client = openai.OpenAI(api_key=api_key)

    prompt = f"""
You are an AI assistant that helps HR rank resumes.

Here is the job description:
\"\"\"{job_desc}\"\"\"

Here is a candidate's resume:
\"\"\"{resume_text}\"\"\"

On a scale of 1 to 100, how well does this resume match the job description? Just give the number, no explanation. Try to give unique and exact numbers so I can rank them later on
"""

    try:
        print("📡 Sending request to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        reply = response.choices[0].message.content.strip()
        print("🧠 GPT reply:", reply)

        # Extract number using regex
        match = re.search(r"\d+(\.\d+)?", reply)
        score = float(match.group()) if match else 0.0
    except Exception as e:
        print("❌ GPT ERROR:", e)
        score = 0.0

    return score

# Streamlit UI
st.set_page_config(page_title="Resume Relevance Ranker", layout="wide")
st.title("📄 Resume Relevance Ranker")

# Sidebar controls
st.sidebar.title("Ranking Options")
ranking_method = st.sidebar.radio("Choose Ranking Method:", ["Cosine Similarity", "GPT-3.5 AI Ranking"])
api_key = st.sidebar.text_input("🔐 Enter your OpenAI API Key", type="password") if ranking_method == "GPT-3.5 AI Ranking" else None

# Main input
job_desc = st.text_area("💼 Enter the Job Description", height=200)
uploaded_files = st.file_uploader("📁 Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# Trigger
if st.button("🚀 Rank Resumes") and uploaded_files:
    if not job_desc.strip():
        st.warning("⚠️ Please enter a job description.")
        st.stop()

    results = []

    with st.spinner("🔍 Processing resumes..."):
        for file in uploaded_files:
            text, links = extract_text_and_links(file)
            link_content = scrape_links(links)
            full_resume_text = text + " " + link_content

            if ranking_method == "Cosine Similarity":
                model = SentenceTransformer("all-MiniLM-L6-v2")
                jd_embed = model.encode([job_desc])
                resume_embed = model.encode([full_resume_text])
                score = cosine_similarity(jd_embed, resume_embed)[0][0] * 10  # Scale to 0–10
            else:
                if not api_key:
                    st.error("Please provide your OpenAI API key.")
                    st.stop()
                print(f"🧪 Using API key: {api_key[:6]}...")  # Masked partial key
                score = gpt_rank_resume(job_desc, full_resume_text[:3000], api_key)

            results.append({"Resume": file.name, "Score": round(score, 2)})
            time.sleep(1.2)  # avoid hitting rate limits

    sorted_results = sorted(results, key=lambda x: x["Score"], reverse=True)
    st.success("✅ Ranking complete!")
    st.subheader("🏆 Top Matching Resumes")
    st.dataframe(sorted_results, use_container_width=True)
