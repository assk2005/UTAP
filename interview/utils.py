import whisper
import re
import cv2
import os
from deepface import DeepFace
from moviepy.video.io.VideoFileClip import VideoFileClip

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from django.conf import settings   # ✅ ADDED (for safe paths)


# ✅ Load models once (safe loading)
model = whisper.load_model("base")
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")


IDEAL_ANSWERS = {

    "Tell me about yourself.":
        "I am a motivated individual with a background in computer science and experience in software development and solving real world problems.",

    "What are your strengths?":
        "My strengths include problem solving, teamwork, adaptability and the ability to quickly learn new technologies.",

    "What are your weaknesses?":
        "One weakness I had was spending too much time perfecting details but I am learning to balance efficiency with quality.",

    "Why should we hire you?":
        "You should hire me because I bring strong technical skills, dedication, and the ability to work effectively in a team.",

    "Where do you see yourself in 5 years?":
        "In five years I see myself growing into a senior role contributing to impactful projects and mentoring junior developers."
}


def extract_audio_from_video(video_path):

    # ✅ Ensure file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    base, ext = os.path.splitext(video_path)

    if ext == "":
        new_video_path = video_path + ".webm"
        if not os.path.exists(new_video_path):
            os.rename(video_path, new_video_path)
        else:
            os.replace(video_path, new_video_path)
        video_path = new_video_path

    video = VideoFileClip(video_path)

    # ✅ Save audio inside MEDIA folder safely
    audio_filename = os.path.basename(video_path).replace(".webm", ".wav")
    audio_path = os.path.join(settings.MEDIA_ROOT, "interview_audio", audio_filename)

    os.makedirs(os.path.dirname(audio_path), exist_ok=True)

    video.audio.write_audiofile(
        audio_path,
        codec="pcm_s16le"
    )

    return audio_path


def convert_speech_to_text(audio_path):

    # ✅ Safety check
    if not os.path.exists(audio_path):
        return ""

    try:
        result = model.transcribe(audio_path)
        return result.get("text", "")
    except Exception as e:
        print("Speech-to-text error:", e)
        return ""


def analyze_emotions(video_path):

    try:

        if not os.path.exists(video_path):
            return "neutral"

        cap = cv2.VideoCapture(video_path)

        emotions_count = {}
        frame_count = 0

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            if frame_count % 60 == 0:

                result = DeepFace.analyze(
                    frame,
                    actions=['emotion'],
                    enforce_detection=False
                )

                emotion = result[0]['dominant_emotion']

                emotions_count[emotion] = emotions_count.get(emotion, 0) + 1

            frame_count += 1

        cap.release()

        if emotions_count:
            return max(emotions_count, key=emotions_count.get)

        return "neutral"

    except Exception as e:

        print("Emotion detection error:", e)

        return "neutral"


def emotion_score(emotion):

    positive = ["happy", "surprise"]
    neutral = ["neutral"]

    if emotion in positive:
        return 3
    elif emotion in neutral:
        return 2
    else:
        return 1


def count_filler_words(text):

    fillers = [
        "um",
        "uh",
        "like",
        "you know",
        "actually",
        "basically",
        "so",
        "well"
    ]

    text = text.lower()

    count = 0

    for word in fillers:
        count += text.count(word)

    return count


def speech_speed(text, duration=60):

    words = len(text.split())

    # ✅ Prevent division error
    if duration == 0:
        return 0

    wpm = (words / duration) * 60

    return round(wpm, 2)


def semantic_answer_score(answer, question):

    ideal_answer = IDEAL_ANSWERS.get(question)

    if not ideal_answer:
        return 5

    try:
        emb1 = semantic_model.encode([answer])
        emb2 = semantic_model.encode([ideal_answer])

        similarity = cosine_similarity(emb1, emb2)[0][0]

        score = similarity * 10

        return float(round(score, 2))

    except Exception as e:
        print("Semantic scoring error:", e)
        return 5


def evaluate_transcript(text, question):

    semantic_score = semantic_answer_score(text, question)

    fillers = count_filler_words(text)

    penalty = min(fillers * 0.2, 2)

    final_score = semantic_score - penalty

    return round(max(final_score, 0), 2)