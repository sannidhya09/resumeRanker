from sentence_transformers import SentenceTransformer, util
import pandas as pd

model = SentenceTransformer("all-MiniLM-L6-v2")

def rank_resumes(resumes, job_description, files):
    job_emb = model.encode(job_description, convert_to_tensor=True)
    resume_embs = model.encode(resumes, convert_to_tensor=True)

    scores = util.cos_sim(job_emb, resume_embs)[0]
    result = sorted(zip([f.name for f in files], scores.tolist()), key=lambda x: x[1], reverse=True)

    df = pd.DataFrame(result, columns=["Resume", "Relevance Score"])
    df["Relevance Score"] = df["Relevance Score"].apply(lambda x: round(x, 4))
    return df
