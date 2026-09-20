from django.urls import path
from . import views

urlpatterns = [
    path('disclaimer/<int:job_id>/', views.disclaimer_page, name='disclaimer'),
    path('start-test/', views.generate_assessment, name="generate_assessment"),
    path('test/', views.test_page, name="test_page"),
    path('api/submit/', views.submit_test, name="submit_test"),
    path('result/<int:result_id>/', views.result_page, name="result_page"),
    path('select-language/', views.select_language, name="select_language"),
    path('start-output-test/', views.start_output_test, name="start_output_test"),
    path('output-test/', views.output_test, name="output_test"),
    path('submit-output-test/', views.submit_output_test, name="submit_output_test"),
    path('final-result/', views.final_result, name="final_result"),
    path('start-test/<int:job_id>/', views.start_test_for_job, name='start_test_for_job'),
]