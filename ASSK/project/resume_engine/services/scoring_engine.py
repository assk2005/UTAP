def compute_final_score(skill_score,experience_score,config):
    final_score=(
        config.skill_weight*skill_score+
        config.experience_weight*experience_score
    )
    return final_score