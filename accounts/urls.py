from django.urls import path,include
from . import views

urlpatterns = [
    # Student
    
    path('student/register/', views.student_register, name='student_register'),
    path('student/login/', views.student_login, name='student_login'),
    path('student/', include('student.urls')),
    


    # Faculty
    path('faculty/register/', views.faculty_register, name='faculty_register'),
    path('faculty/login/', views.faculty_login, name='faculty_login'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/exams/', views.faculty_exams, name='faculty_exams'),
    path('faculty/exams/add/', views.add_exam, name='add_exam'),
path(
    'faculty/exams/<int:exam_id>/questions/',
    views.add_exam_questions,
    name='add_exam_questions'
),

path(
    'faculty/exams/<int:exam_id>/questions/<int:question_id>/edit/',
    views.edit_exam_question,
    name='edit_exam_question'
),

path(
    'faculty/exams/<int:exam_id>/questions/<int:question_id>/delete/',
    views.delete_exam_question,
    name='delete_exam_question'
),

path(
    'faculty/exams/<int:exam_id>/results/',
    views.exam_results,
    name='exam_results'
),
path(
    'faculty/exams/<int:exam_id>/preview/',
    views.preview_exam,
    name='preview_exam'
),
path('faculty/students/pdf/', views.download_students_pdf, name='download_students_pdf'),

path('faculty/profile/', views.faculty_profile, name='faculty_profile'),
path('faculty/profile/edit/', views.edit_faculty_profile, name='edit_faculty_profile'),


path('faculty/exam/<int:exam_id>/start/', views.faculty_start_exam, name='faculty_start_exam'),

path('faculty/exams/<int:exam_id>/stop/', views.stop_exam, name='stop_exam'),
path('faculty/exams/<int:exam_id>/monitor/', views.monitor_exam, name='monitor_exam'),
path('faculty/exams/<int:exam_id>/results/',views.exam_results,name='exam_results'
),


    path('faculty/students/', views.faculty_students, name='faculty_students'),
    path('faculty/profile/', views.faculty_profile, name='faculty_profile'),
    path('faculty/students/<int:student_id>/', views.faculty_student_detail, name='faculty_student_detail'),
     path('faculty/student/delete/<int:student_id>/', views.faculty_delete_student, name='faculty_delete_student'),

    path("admin/login/", views.admin_login, name="admin_login"),
    path("logout/", views.user_logout, name="logout"),  # ✅ ADD THIS
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/approve/<int:profile_id>/", views.approve_faculty, name="approve_faculty"),
    path("admin/reject/<int:profile_id>/", views.reject_faculty, name="reject_faculty"),

]
