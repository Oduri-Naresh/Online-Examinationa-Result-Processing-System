from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Exam, Question, ExamAttempt, StudentAnswer
from accounts.models import StudentProfile

def starts_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, status='active')
    student = request.user.studentprofile

    attempt = ExamAttempt.objects.create(
        student=student,
        exam=exam
    )

    for q in Question.objects.filter(exam=exam):
        StudentAnswer.objects.create(attempt=attempt, question=q)

    return redirect('exam_attempt', attempt_id=attempt.id)

def exam_attempt(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, is_submitted=False)
    questions = Question.objects.filter(exam=attempt.exam).order_by('id')
    answers = StudentAnswer.objects.filter(attempt=attempt)

    question_map = {
        ans.question.id: ans.selected_option for ans in answers
    }

    return render(request, 'student/exam_attempt.html', {
        'attempt': attempt,
        'questions': questions,
        'question_map': question_map,
        'duration': attempt.exam.duration
    })
def submit_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    attempt.is_submitted = True
    attempt.save()
    return redirect('student_dashboard')
