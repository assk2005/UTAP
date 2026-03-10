import numpy as np
from sentence_transformers import SentenceTransformer
from resume_engine.services.preprocessing import clean_text
import re

model=SentenceTransformer('all-MiniLM-L6-v2')


def split_sentences(text):
    return re.split(r'\n+|\.|\•|\-', text)


def cosine_similarity(vec1,vec2):
    return np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))


def evaluate_skills(resume_text,skills_list,config):
    resume_text=clean_text(resume_text)
    sentences=split_sentences(resume_text)

    sentence_embeddings=model.encode(sentences)

    total_strength=0

    for skill in skills_list:
        skill=skill.strip().lower()
        skill_embedding=model.encode([skill])[0]

        max_similarity=0
        occurrence_count=0

        for i,sentence in enumerate(sentences):
            if skill in sentence:
                occurrence_count+=1

            sim=cosine_similarity(skill_embedding,sentence_embeddings[i])

            if sim>max_similarity:
                max_similarity=sim

        S1=max_similarity

        S2=min(occurrence_count/3,1.0)

        if occurrence_count >= 2:
            S3 = 1.0
        elif occurrence_count == 1:
            S3 = 0.7
        else:
            S3 = 0.4

        S4=1.0

        skill_strength=(
            config.semantic_weight*S1+
            config.frequency_weight*S2+
            config.context_weight*S3+
            config.recency_weight*S4
        )

        total_strength+=skill_strength

    if len(skills_list)==0:
        return 0

    return total_strength/len(skills_list)