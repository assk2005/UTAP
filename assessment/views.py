from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
from accounts.models import Job
import random
import json
from django.views.decorators.csrf import csrf_exempt
import os
from assessment.models import TestResult
from django.contrib import messages
from accounts.models import Application
TEST_DURATION = 600
PASS_PERCENTAGE = 70

def disclaimer_page(request, job_id):
    from accounts.models import Job
    job = Job.objects.get(id=job_id)
    return render(request, "assessment/disclaimer.html", {
        "job": job
    })


def get_random_questions(model, count):
    questions = list(model.objects.all())
    random.shuffle(questions)
    return questions[:count]


def test_page(request):

    job_id = request.session.get("job_id")

    if not job_id:
        return redirect("candidate_dashboard")
    
    questions = request.session.get("questions", [])

    return render(request, "assessment/test.html", {
        "questions": questions,
        "duration": TEST_DURATION
    })


@csrf_exempt
def submit_test(request):

    if request.method == "POST":
        try:
            body = json.loads(request.body)
            answers = body.get("answers", {})

            questions = request.session.get("questions", [])

            if not questions:
                return JsonResponse({"error": "No questions found"}, status=400)

            score = 0
            total = len(questions)

            for index, selected_option in answers.items():
                try:
                    q_index = int(index)
                    correct_option = questions[q_index].get("correct")

                    if correct_option is None:
                        continue

                    if int(selected_option) == int(correct_option):
                        score += 1

                except Exception as e:
                    print("Question error:", e)
                    continue

            percentage = (score / total) * 100 if total > 0 else 0

            print("FINAL SCORE:", score)

            request.session["mcq_score"] = score
            request.session["mcq_total"] = total

            job_id = request.session.get("job_id")
            job = Job.objects.get(id=job_id)

            if job.coding_required:
                redirect_url = "/assessment/select-language/"
            else:
                redirect_url = "/assessment/final-result/"

            return JsonResponse({
                "redirect_url": redirect_url
            })

        except Exception as e:
            print("ERROR IN SUBMIT:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


def result_page(request, result_id):
    result = TestResult.objects.get(id=result_id)

    qualified = result.percentage >= PASS_PERCENTAGE

    return render(request, "assessment/result.html", {
        "result": result,
        "qualified": qualified,
    })

def generate_assessment(request):

    MAX_TOTAL = 30

    job_id = request.session.get("job_id")

    if not job_id:
        return redirect("candidate_dashboard")

    job = Job.objects.get(id=job_id)

# adjust field name based on your model
    skills_raw = job.skills_required

    skills = [s.strip().lower() for s in skills_raw.split(",")]

    if not skills:
        return redirect("test_page")

    final_questions = []

    # Equal distribution
    questions_per_skill = MAX_TOTAL // len(skills)

    for skill in skills:

        question_file_path = os.path.join(
            "assessment",
            "question_bank",
            f"{skill.replace(' ', '_')}.json"
        )

        if os.path.exists(question_file_path):

            with open(question_file_path, "r") as qfile:
                questions = json.load(qfile)

            selected = random.sample(
                questions,
                min(questions_per_skill, len(questions))
            )

            final_questions.extend(selected)

    # If total is less than 30 (because some skill had fewer questions)
    if len(final_questions) < MAX_TOTAL:

        remaining_needed = MAX_TOTAL - len(final_questions)

        all_extra = []

        for skill in skills:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            question_file_path = os.path.join(
                BASE_DIR,
                "assessment",
                "question_bank",
                f"{skill.replace(' ', '_')}.json"
            )

            if os.path.exists(question_file_path):
                with open(question_file_path, "r") as qfile:
                    questions = json.load(qfile)
                    all_extra.extend(questions)

        additional = random.sample(
            all_extra,
            min(remaining_needed, len(all_extra))
        )

        final_questions.extend(additional)

    random.shuffle(final_questions)

    request.session["questions"] = final_questions

    return redirect("test_page")

def select_language(request):
    return render(request, "assessment/select_language.html")

def start_output_test(request):

    language = request.POST.get("language")

    request.session["language"] = language

    return redirect("output_test")


def load_output_questions(language):

    file_path = os.path.join(
        "assessment",
        "output_questions",
        f"{language}.json"
    )

    with open(file_path, "r") as f:
        questions = json.load(f)

    # select 10 random questions
    return random.sample(questions, 10)

def output_test(request):

    language = request.session.get("language")

    questions = load_output_questions(language)

    request.session["output_questions"] = questions

    return render(request,"assessment/output_test.html",{
        "questions":questions
    })

@csrf_exempt



def submit_output_test(request):

    if request.method == "POST":

        body = json.loads(request.body)

        answers = body.get("answers", {})

        questions = request.session.get("output_questions", [])

        score = 0
        total = len(questions)

        for i, selected in answers.items():

            correct = questions[int(i)]["answer"]

            if int(selected) == int(correct):
                score += 1

        request.session["output_score"] = score
        request.session["output_total"] = total

        return JsonResponse({
            "redirect_url": "/assessment/final-result/"
        })


def final_result(request):

    user = request.user
    job_id = request.session.get("job_id")
    job = Job.objects.get(id=job_id)

    mcq_score = request.session.get("mcq_score", 0)
    mcq_total = request.session.get("mcq_total", 30)

    output_score = request.session.get("output_score", 0)
    output_total = request.session.get("output_total", 10)

    app = Application.objects.filter(candidate=user, job=job).first()
    resume_score = app.score if app and app.score else 0

    mcq_percent = (mcq_score / mcq_total) * 100 if mcq_total else 0
    output_percent = (output_score / output_total) * 100 if output_total else 0

    RESUME_W = 0.4
    MCQ_W = 0.3
    OUTPUT_W = 0.3

    if job.coding_required:
        overall = (
            resume_score * RESUME_W +
            mcq_percent * MCQ_W +
            output_percent * OUTPUT_W
        )
    else:
        total_w = RESUME_W + MCQ_W
        overall = (
            (resume_score * RESUME_W) +
            (mcq_percent * MCQ_W)
        ) / total_w

    overall = round(overall, 2)

    # SAVE RESULT
    TestResult.objects.update_or_create(
        candidate=user,
        job=job,
        defaults={
            "mcq_score": mcq_score,
            "mcq_total": mcq_total,
            "output_score": output_score,
            "output_total": output_total,
            "final_score": overall,
            "percentage": overall
        }
    )
    Application.objects.filter(
        candidate=user,
        job=job
    ).update(test_completed=True)

    # ✅ PASS/FAIL LOGIC
    passed = overall >= 70

    return render(request, "assessment/final_result.html", {
        "passed": passed
    })
def start_test_for_job(request, job_id):
    request.session["job_id"] = job_id
    return redirect("disclaimer", job_id=job_id)