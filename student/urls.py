from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.student_profile, name='student_profile'),
    path('profile/edit/', views.edit_student_profile, name='edit_student_profile'),
    path('available-exams/', views.available_exams, name='available_exams'),
    path('exam/<int:exam_id>/start/', views.start_exam, name='student_start_exam'),
    path('exam-history/', views.exam_history, name='exam_history'),
    path('attempt/<int:attempt_id>/', views.exam_attempt, name='exam_attempt'),
    path('submit/<int:attempt_id>/', views.submit_exam, name='submit_exam'),
    path('attempt/<int:attempt_id>/submit/', views.submit_exam, name='submit_exam'),

    
]   
