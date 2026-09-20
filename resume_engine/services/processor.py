from resume_engine.services.text_extractor import extract_text
from resume_engine.services.preprocessing import is_english,anonymize_text,clean_text
from resume_engine.services.experience_engine import extract_experience,compute_experience_score
from resume_engine.services.semantic_engine import evaluate_skills
from resume_engine.services.scoring_engine import compute_final_score
from resume_engine.models import EngineConfig


def evaluate_application(application):

    resume_path=application.resume.path

    raw_text=extract_text(resume_path)

    if not raw_text or len(raw_text)<50 or not is_english(raw_text):
        return {
            "skill_score":0,
            "experience_score":0,
            "final_score":0
        }

    anonymized=anonymize_text(raw_text)
    cleaned=clean_text(anonymized)

    onsite,remote=extract_experience(cleaned)

    adjusted,exp_score=compute_experience_score(
        onsite,
        remote,
        application.job.min_experience
    )

    skills_list=[
        skill.strip()
        for skill in application.job.skills_required.split(',')
        if skill.strip()
    ]

    config=EngineConfig.objects.first()

    if not config:
        raise ValueError("EngineConfig not configured")

    skill_score=evaluate_skills(cleaned,skills_list,config)

    final_score=compute_final_score(skill_score,exp_score,config)

    print("Skill Score:",skill_score)
    print("Experience Score:",exp_score)
    print("Final Score:",final_score)

    return {
        "skill_score":skill_score,
        "experience_score":exp_score,
        "final_score":final_score
    }