from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Job, Application, RecruiterProfile
from .serializers import JobSerializer
from .permissions import IsRecruiter, IsCandidate, IsAdmin

from django.views.decorators.cache import never_cache
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator

@never_cache
def custom_logout(request):
    logout(request)
    response = HttpResponseRedirect(reverse('login'))
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

User = get_user_model()


# ================= REGISTER VIEW (HTML BASED) =================

class RegisterView(View):

    def get(self,request):
        return render(request,'accounts/register.html')

    def post(self,request):
        role=request.POST.get('role')

        if role=='candidate':
            email=request.POST.get('reg_email')
            password=request.POST.get('reg_password')
            confirm_password=request.POST.get('reg_confirm_password')

            if not email:
                messages.error(request,"Email is required.")
                return redirect('register')

            if password!=confirm_password:
                messages.error(request,"Passwords do not match.")
                return redirect('register')

            if User.objects.filter(email=email).exists():
                messages.error(request,"Email already registered.")
                return redirect('register')

            user=User.objects.create_user(
                email=email,
                password=password,
                role='candidate'
            )
            user.is_active=True
            user.save()

            messages.success(request,"Account created successfully. Please login.")
            return redirect('login')

        elif role=='recruiter':
            email=request.POST.get('rec_email')
            password=request.POST.get('rec_password')
            confirm_password=request.POST.get('rec_confirm_password')

            if not email:
                messages.error(request,"Email is required.")
                return redirect('register')

            if password!=confirm_password:
                messages.error(request,"Passwords do not match.")
                return redirect('register')

            if User.objects.filter(email=email).exists():
                messages.error(request,"Email already registered.")
                return redirect('register')

            user=User.objects.create_user(
                email=email,
                password=password,
                role='recruiter'
            )
            user.is_active=False
            user.save()

            RecruiterProfile.objects.create(
                user=user,
                full_name=request.POST.get('rec_full_name'),
                designation=request.POST.get('rec_designation'),
                phone=request.POST.get('rec_phone'),
                linkedin_url=request.POST.get('rec_linkedin'),
                company_name=request.POST.get('rec_company_name'),
                company_website=request.POST.get('rec_company_website'),
                company_location=request.POST.get('rec_company_location'),
                industry_type=request.POST.get('rec_industry'),
                company_size=request.POST.get('rec_company_size'),
                is_verified=False
            )

            messages.success(
                request,
                "Recruiter registration submitted. Admin approval required before login."
            )
            return redirect('login')

        messages.error(request,"Invalid role selected.")
        return redirect('register')


# ================= PUBLIC PAGES =================

def home(request):
    return render(request, 'accounts/home.html')


def about(request):
    return render(request, 'accounts/about.html')


def recruiters_page(request):
    return render(request, 'accounts/recruiters.html')


def candidates_page(request):
    return render(request, 'accounts/candidates.html')


# ================= API VIEWS =================

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "JWT is working"})


class RecruiterOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]

    def get(self, request):
        return Response({"message": "Recruiter access granted"})


class CandidateOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):
        return Response({"message": "Candidate access granted"})


class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({"message": "Admin access granted"})


class RecruiterJobCreateView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]

    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(recruiter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecruiterJobListView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]

    def get(self, request):
        jobs = Job.objects.filter(recruiter=request.user)
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)


# ================= REDIRECT LOGIC =================

@never_cache
@login_required
def home_redirect(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    if request.user.role == 'recruiter':
        return redirect('recruiter_dashboard')
    if request.user.role == 'candidate':
        return redirect('candidate_job_list')
    return redirect('login')


# ================= RECRUITER UI =================

@never_cache
@login_required
def job_create_ui(request):
    if request.user.role!='recruiter':
        return redirect('home_redirect')

    if request.method=='POST':

        try:
            min_exp=int(request.POST['min_experience'])
            max_exp=int(request.POST['max_experience'])
        except:
            messages.error(request,"Invalid experience values.")
            return redirect('job_create_ui')

        if min_exp<0 or max_exp<0:
            messages.error(request,"Experience cannot be negative.")
            return redirect('job_create_ui')

        if min_exp>max_exp:
            messages.error(request,"Minimum experience cannot be greater than maximum experience.")
            return redirect('job_create_ui')

        salary_min=request.POST.get('salary_min')
        salary_max=request.POST.get('salary_max')

        if salary_min:
            salary_min=int(salary_min)
            if salary_min<0:
                messages.error(request,"Salary cannot be negative.")
                return redirect('job_create_ui')

        if salary_max:
            salary_max=int(salary_max)
            if salary_max<0:
                messages.error(request,"Salary cannot be negative.")
                return redirect('job_create_ui')

        if salary_min and salary_max and salary_min>salary_max:
            messages.error(request,"Minimum salary cannot exceed maximum salary.")
            return redirect('job_create_ui')

        Job.objects.create(
            recruiter=request.user,
            company_name=request.POST['company_name'],
            title=request.POST['title'],
            description=request.POST['description'],
            location=request.POST['location'],
            skills_required=request.POST['skills_required'],
            min_experience=min_exp,
            max_experience=max_exp,
            employment_type=request.POST['employment_type'],
            salary_min=salary_min or None,
            salary_max=salary_max or None,
            coding_required=True if request.POST.get('coding_required') else False,
            application_deadline=request.POST['application_deadline']
        )

        return redirect('recruiter_dashboard')

    return render(request,'accounts/job_create.html')


@never_cache
@login_required
def recruiter_dashboard(request):
    if request.user.role!='recruiter':
        return redirect('home_redirect')

    profile=RecruiterProfile.objects.get(user=request.user)

    if not profile.is_verified:
        return render(request,'accounts/recruiter_pending.html')

    jobs=Job.objects.filter(recruiter=request.user)

    job_data=[]

    for job in jobs:
        applications=Application.objects.filter(job=job)

        job_data.append({
            "job":job,
            "total":applications.count(),
            "shortlisted":applications.filter(status='shortlisted').count(),
            "selected":applications.filter(status='selected').count()
        })

    return render(request,'accounts/recruiter_dashboard.html',{
        "job_data":job_data,
        "total_jobs":jobs.count(),
        "active_jobs":jobs.filter(status='active').count(),
        "closed_jobs":jobs.filter(status='closed').count()
    })


@never_cache
@login_required
def recruiter_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = Application.objects.filter(job=job).order_by('-score')
    return render(request, 'accounts/recruiter_applications.html', {
        'job': job,
        'applications': applications
    })


# ================= CANDIDATE UI =================

@never_cache
@login_required
def candidate_job_list(request):
    jobs = Job.objects.filter(status='active')

    applied_job_ids = Application.objects.filter(
        candidate=request.user
    ).values_list('job_id', flat=True)

    context = {
        'jobs': jobs,
        'applied_job_ids': list(applied_job_ids)
    }

    return render(request, 'accounts/candidate_job_list.html', context)


@never_cache
@login_required
def apply_to_job(request, job_id):

    if request.user.role != 'candidate':
        return redirect('home_redirect')

    job = get_object_or_404(Job, id=job_id, status='active')

    # Check if already applied
    existing_application = Application.objects.filter(
        candidate=request.user,
        job=job
    ).first()

    if existing_application:
        messages.warning(
            request,
            'You have already applied to this job.'
        )
        return redirect('candidate_dashboard')

    # Create new application
    application = Application.objects.create(
        candidate=request.user,
        job=job,
        status='applied'
    )

    messages.success(
        request,
        'Application submitted successfully. Please upload your resume to start evaluation.'
    )

    # Redirect directly to upload page
    return redirect('upload_resume', application_id=application.id)

@never_cache
@login_required
def candidate_dashboard(request):
    applications = Application.objects.filter(candidate=request.user)

    context = {
        'applications': applications,
        'total_available_jobs': Job.objects.filter(status='active').count(),
        'total_applications': applications.count(),
        'shortlisted_count': applications.filter(status='shortlisted').count(),
        'selected_count': applications.filter(status='selected').count(),
        'rejected_count': applications.filter(status='rejected').count(),
    }

    return render(request, 'accounts/candidate_dashboard.html', context)


@never_cache
@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, status='active')

    already_applied = Application.objects.filter(
        candidate=request.user,
        job=job
    ).exists()

    return render(request, 'accounts/job_detail.html', {
        'job': job,
        'already_applied': already_applied
    })


@never_cache
@login_required
def upload_resume(request, application_id):

    if request.user.role != 'candidate':
        return redirect('home_redirect')

    application = get_object_or_404(
        Application,
        id=application_id,
        candidate=request.user
    )

    if request.method == 'POST':

        from resume_engine.services.processor import evaluate_application

        application.resume = request.FILES['resume']
        application.save()

        result = evaluate_application(application)

        application.score = round(result["final_score"] * 100)

        cutoff = application.job.cutoff_score or 35

        if application.score >= cutoff:
            application.status = 'shortlisted'
        else:
            application.status = 'rejected'

        application.save()

        messages.success(
            request,
            f'Resume evaluated successfully. Score: {application.score}'
        )

        return redirect('candidate_dashboard')

    return render(
        request,
        'accounts/upload_resume.html',
        {'application': application}
    )


# ================= ADMIN =================

@never_cache
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    context = {
        "total_candidates": User.objects.filter(role='candidate').count(),
        "total_recruiters": User.objects.filter(role='recruiter').count(),
        "total_jobs": Job.objects.count(),
        "total_applications": Application.objects.count(),
        "pending_recruiters": RecruiterProfile.objects.filter(is_verified=False).count(),
        "recent_users": User.objects.order_by('-created_at')[:5]
    }

    return render(request, 'accounts/admin_dashboard.html', context)

from django.contrib.auth.views import LoginView
from django.urls import reverse

class CustomLoginView(LoginView):
    template_name='registration/login.html'

    def get_success_url(self):
        user=self.request.user

        if user.is_superuser:
            return reverse('admin_dashboard')
        elif user.role=='recruiter':
            return reverse('recruiter_dashboard')
        elif user.role=='candidate':
            return reverse('candidate_dashboard')
        return reverse('home')
    
@never_cache
@login_required
def admin_recruiters(request):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    recruiters = RecruiterProfile.objects.select_related('user').all()

    return render(request, 'accounts/admin_recruiters.html', {
        'recruiters': recruiters
    })


@never_cache
@login_required
def verify_recruiter(request, pk):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    recruiter = get_object_or_404(RecruiterProfile, id=pk)
    recruiter.is_verified = True
    recruiter.save()

    recruiter.user.is_active = True
    recruiter.user.save()

    messages.success(request, "Recruiter verified successfully.")
    return redirect('admin_recruiters')


@never_cache
@login_required
def delete_recruiter(request, pk):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    recruiter = get_object_or_404(RecruiterProfile, id=pk)
    recruiter.user.delete()

    messages.success(request, "Recruiter deleted successfully.")
    return redirect('admin_recruiters')

@never_cache
@login_required
def admin_candidates(request):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    candidates = User.objects.filter(role='candidate').prefetch_related('applications')

    return render(request, 'accounts/admin_candidates.html', {
        'candidates': candidates
    })


@never_cache
@login_required
def delete_candidate(request, pk):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    candidate = get_object_or_404(User, id=pk, role='candidate')
    candidate.delete()

    messages.success(request, "Candidate deleted successfully.")
    return redirect('admin_candidates')

@never_cache
@login_required
def admin_applications(request):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    applications = Application.objects.select_related('candidate', 'job').order_by('-id')

    return render(request, 'accounts/admin_applications.html', {
        'applications': applications
    })


@never_cache
@login_required
def delete_application(request, pk):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    application = get_object_or_404(Application, id=pk)
    application.delete()

    messages.success(request, "Application deleted successfully.")
    return redirect('admin_applications')

@never_cache
@login_required
def toggle_recruiter_status(request, pk):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    recruiter = get_object_or_404(RecruiterProfile, id=pk)

    recruiter.user.is_active = not recruiter.user.is_active
    recruiter.user.save()

    return redirect('admin_recruiters')

@never_cache
@login_required
def toggle_candidate_status(request, pk):
    if not request.user.is_superuser:
        return redirect('home_redirect')

    candidate = get_object_or_404(User, id=pk, role='candidate')

    candidate.is_active = not candidate.is_active
    candidate.save()

    return redirect('admin_candidates')