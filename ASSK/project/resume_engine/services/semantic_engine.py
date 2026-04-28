import numpy as np
from sentence_transformers import SentenceTransformer
from resume_engine.services.preprocessing import clean_text
import re
from datetime import datetime

model=SentenceTransformer('all-MiniLM-L6-v2')


def split_sentences(text):
    return re.split(r'[.\n•]',text)


def cosine_similarity(vec1,vec2):
    return np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))


def skill_present(skill,sentence):
    pattern=r'\b'+re.escape(skill)+r'\b'
    return bool(re.search(pattern,sentence,re.IGNORECASE))


def compute_recency_score(resume_text):

    year_matches=re.findall(r'20\d{2}',resume_text)

    if not year_matches:
        return 0.8

    latest_year=max(map(int,year_matches))
    current_year=datetime.now().year

    diff=current_year-latest_year

    if diff<=1:
        return 1.0
    elif diff<=3:
        return 0.8
    elif diff<=5:
        return 0.6
    else:
        return 0.3


def evaluate_skills(resume_text,skills_list,config):

    resume_text=clean_text(resume_text)

    sentences=split_sentences(resume_text)

    sentence_embeddings=model.encode(sentences)

    S4=compute_recency_score(resume_text)

    total_strength=0

    for skill in skills_list:

        skill=skill.strip().lower()

        skill_embedding=model.encode([skill])[0]

        max_similarity=0
        occurrence_count=0

        for i,sentence in enumerate(sentences):

            if skill_present(skill,sentence):
                occurrence_count+=1

            sim=cosine_similarity(skill_embedding,sentence_embeddings[i])

            if sim>max_similarity:
                max_similarity=sim

        S1=max_similarity

        S2=min(occurrence_count/3,1.0)

        if occurrence_count>=2:
            S3=1.0
        elif occurrence_count==1:
            S3=0.7
        else:
            S3=0.4

        skill_strength=(
            config.semantic_weight*S1+
            config.frequency_weight*S2+
            config.context_weight*S3+
            config.recency_weight*S4
        )

        print(
            f"Skill: {skill} | "
            f"S1:{S1:.3f} "
            f"S2:{S2:.3f} "
            f"S3:{S3:.3f} "
            f"S4:{S4:.3f} "
            f"Strength:{skill_strength:.3f}"
        )

        total_strength+=skill_strength


    if len(skills_list)==0:
        return 0

    return total_strength/len(skills_list)