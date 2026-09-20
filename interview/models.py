from django.db import models
from django.conf import settings   



class InterviewSession(models.Model):
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pending")
    final_score = models.FloatField(null=True, blank=True)

    # ✅ OPTIONAL (for integration with assessment)
    # assessment_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Interview {self.id} - {self.candidate.username}"


class AudioInterviewResponse(models.Model):
    interview = models.ForeignKey(InterviewSession, on_delete=models.CASCADE)

    question = models.TextField()

    video_file = models.FileField(
        upload_to='interview_videos/',   # already correct (will go inside MEDIA_ROOT)
        null=True,
        blank=True
    )

    transcript = models.TextField(null=True, blank=True)

    # AI evaluation fields
    score = models.FloatField(null=True, blank=True)
    emotion = models.CharField(max_length=20, null=True, blank=True)

    filler_words = models.IntegerField(null=True, blank=True)
    speech_speed = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ ADDED (for better querying + performance)
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Response for Interview {self.interview.id}"


class InterviewQuestion(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE)

    question_text = models.TextField()

    order = models.IntegerField(default=1)

    # ✅ ADDED (ensures correct question order per session)
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Question {self.order} - Interview {self.session.id}"