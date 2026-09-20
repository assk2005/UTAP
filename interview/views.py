from django.shortcuts import render
from django.http import JsonResponse

from django.conf import settings
import os

from .models import InterviewSession, AudioInterviewResponse
from .utils import (
    convert_speech_to_text,
    evaluate_transcript,
    extract_audio_from_video,
    analyze_emotions,
    emotion_score,
    count_filler_words,
    speech_speed
)


HR_QUESTIONS = [
    "Tell me about yourself.",
    "What are your strengths?",
    "What are your weaknesses?",
    "Why should we hire you?",
    "Where do you see yourself in 5 years?",
]


def interview_home(request):
    return render(request, "interview/home.html")


def start_interview(request):

    # ✅ FIXED: Use logged-in user (custom user model safe)
    user = request.user

    # Optional (no logic change)
    if not user or not user.is_authenticated:
        # fallback if user not logged in
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.first()

    assessment_score = request.GET.get("score", None)

    session = InterviewSession.objects.create(
        candidate=user,
        # assessment_score=assessment_score
    )

    return render(request, "interview/interview.html", {
        "session": session,
        "question_text": HR_QUESTIONS[0],
        "question_index": 0
    })


def upload_audio(request, session_id):

    try:
        session = InterviewSession.objects.get(id=session_id)
    except InterviewSession.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)

    media_audio_path = os.path.join(settings.MEDIA_ROOT, "interview_audio")
    os.makedirs(media_audio_path, exist_ok=True)

    if request.method == "POST":

        video = request.FILES["audio"]
        question = request.POST["question"]
        question_index = int(request.POST["question_index"])

        response = AudioInterviewResponse.objects.create(
            interview=session,
            question=question,
            video_file=video
        )

        video_path = response.video_file.path

        if not os.path.exists(video_path):
            return JsonResponse({"error": "File not saved correctly"}, status=400)

        audio_path = extract_audio_from_video(video_path)

        transcript = convert_speech_to_text(audio_path)

        if not transcript:
            transcript = ""

        filler_count = count_filler_words(transcript)
        wpm = speech_speed(transcript)

        emotion = analyze_emotions(video_path)
        emotion_points = emotion_score(emotion)

        semantic_score = evaluate_transcript(transcript, question)

        final_score = round(min(semantic_score + emotion_points, 10), 2)

        response.transcript = transcript
        response.score = final_score
        response.emotion = emotion
        response.filler_words = filler_count
        response.speech_speed = wpm
        response.save()

        next_index = question_index + 1

        if next_index < len(HR_QUESTIONS):

            next_question = HR_QUESTIONS[next_index]
            interview_complete = False

        else:

            next_question = "Interview Completed. Thank you!"
            interview_complete = True

            responses = AudioInterviewResponse.objects.filter(interview=session)

            total_score = sum(r.score for r in responses)
            avg_score = total_score / len(responses)

            session.final_score = round(avg_score, 2)
            session.status = "completed"
            session.save()

        return JsonResponse({
            "transcript": transcript,
            "score": float(final_score),
            "emotion": str(emotion),
            "filler_words": int(filler_count),
            "speech_speed": float(wpm),
            "next_question": str(next_question),
            "next_index": int(next_index),
            "complete": bool(interview_complete)
        })


def interview_result(request):

    session = InterviewSession.objects.last()

    responses = AudioInterviewResponse.objects.filter(interview=session)

    if not responses:
        return render(request, "interview/result.html", {
            "score": 0,
            "responses": [],
            "fillers": 0,
            "speech_speed": 0,
            "emotions": []
        })

    total_score = 0
    total_fillers = 0
    total_wpm = 0
    emotion_list = []

    for r in responses:
        total_score += r.score
        total_fillers += r.filler_words
        total_wpm += r.speech_speed
        emotion_list.append(r.emotion)

    avg_score = round(total_score / len(responses), 2)
    avg_wpm = round(total_wpm / len(responses), 2)

    return render(request, "interview/result.html", {
        "score": avg_score,
        "responses": responses,
        "fillers": total_fillers,
        "speech_speed": avg_wpm,
        "emotions": emotion_list
    })