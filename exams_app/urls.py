from django.urls import path
from . import views

urlpatterns = [
    path('starts/<int:exam_id>/', views.starts_exam, name='starts_exam'),
    path('attempt/<int:attempt_id>/', views.exam_attempt, name='exam_attempt'),
    path('submit/<int:attempt_id>/', views.submit_exam, name='submit_exam'),
]
