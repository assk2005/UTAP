from django.contrib import admin
from .models import EngineConfig


@admin.register(EngineConfig)
class EngineConfigAdmin(admin.ModelAdmin):
    list_display = (
        "similarity_threshold",
        "skill_weight",
        "experience_weight",
        "min_final_score",
        "semantic_weight",
        "frequency_weight",
        "context_weight",
        "recency_weight",
    )