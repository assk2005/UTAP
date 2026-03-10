from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.db import models
from django.utils import timezone
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self,email,password=None,role='candidate'):
        if not email:
            raise ValueError('Email is required')
        user=self.model(
            email=self.normalize_email(email),
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None):
        user=self.create_user(
            email=email,
            password=password,
            role='admin'
        )
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser,PermissionsMixin):
    ROLE_CHOICES=(
        ('candidate','Candidate'),
        ('recruiter','Recruiter'),
        ('admin','Admin'),
    )

    email=models.EmailField(unique=True)
    role=models.CharField(max_length=20,choices=ROLE_CHOICES)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    created_at=models.DateTimeField(default=timezone.now)

    objects=UserManager()

    USERNAME_FIELD='email'

    def __str__(self):
        return self.email
    
from django.conf import settings
from django.db import models
from django.utils import timezone

class Job(models.Model):
    STATUS_CHOICES=(
        ('active','Active'),
        ('closed','Closed'),
    )

    EMPLOYMENT_CHOICES=(
        ('internship','Internship'),
        ('full_time','Full Time'),
        ('contract','Contract'),
    )

    recruiter=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='jobs')
    company_name=models.CharField(max_length=255)
    title=models.CharField(max_length=255)
    description=models.TextField()
    location=models.CharField(max_length=255)
    skills_required=models.TextField()
    min_experience = models.PositiveIntegerField()
    max_experience = models.PositiveIntegerField()
    employment_type=models.CharField(max_length=20,choices=EMPLOYMENT_CHOICES)
    salary_min=models.IntegerField(null=True,blank=True)
    salary_max=models.IntegerField(null=True,blank=True)
    coding_required=models.BooleanField(default=False)
    cutoff_score=models.IntegerField(null=True,blank=True)
    application_deadline=models.DateField()
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='active')
    created_at=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES=(
        ('applied','Applied'),
        ('shortlisted','Shortlisted'),
        ('rejected','Rejected'),
        ('selected','Selected'),
    )

    candidate=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='applications')
    job=models.ForeignKey('Job',on_delete=models.CASCADE,related_name='applications')

    # Profile Information
    full_name=models.CharField(max_length=200,null=True,blank=True)
    phone=models.CharField(max_length=15,null=True,blank=True)
    education=models.CharField(max_length=255,null=True,blank=True)
    experience=models.IntegerField(null=True,blank=True)
    skills=models.TextField(null=True,blank=True)

    # Resume + Evaluation
    resume=models.FileField(upload_to='resumes/',null=True,blank=True)
    score=models.IntegerField(null=True,blank=True)

    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='applied')
    applied_at=models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together=('candidate','job')

    def __str__(self):
        return f'{self.candidate.email} - {self.job.title}'

class RecruiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recruiter_profile')

    # Personal Details
    full_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    linkedin_url = models.URLField(blank=True)

    # Company Details
    company_name = models.CharField(max_length=255)
    company_website = models.URLField(blank=True)
    company_location = models.CharField(max_length=255)
    industry_type = models.CharField(max_length=255)
    company_size = models.CharField(max_length=100)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company_name} - {self.user.email}"