from django.db import models

class EngineConfig(models.Model):
    similarity_threshold=models.FloatField(default=0.7)

    skill_weight=models.FloatField(default=0.7)
    experience_weight=models.FloatField(default=0.3)

    min_final_score=models.FloatField(default=0.35)

    semantic_weight=models.FloatField(default=0.5)
    frequency_weight=models.FloatField(default=0.2)
    context_weight=models.FloatField(default=0.2)
    recency_weight=models.FloatField(default=0.1)

    def __str__(self):
        return "Resume Engine Configuration"