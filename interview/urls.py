from django.urls import path
from . import views

urlpatterns = [
    # Landing Page
    path("", views.interview_home, name="interview_home"),

    # Interview Screen
    path("start/", views.start_interview, name="start_interview"),

    # ✅ ADDED (allows passing session id / future flexibility)
    path("start/<int:session_id>/", views.start_interview, name="start_interview_with_id"),

    # Upload API
    path("upload/<int:session_id>/", views.upload_audio, name="upload_audio"),

    # Result Page
    path("result/", views.interview_result, name="interview_result"),
]