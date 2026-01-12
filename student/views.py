from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth

from exams_app.models import Exam, ExamAttempt, StudentAnswer
from accounts.models import Profile


# =========================
# STUDENT DASHBOARD
# =========================
@login_required
def student_dashboard(request):
    student = request.user.profile

    attempts = (
        ExamAttempt.objects
        .filter(student=student)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months = []
    counts = []

    for item in attempts:
        months.append(item['month'].strftime('%b %Y'))
        counts.append(item['count'])

    context = {
        'student': student,
        'months': months,
        'counts': counts,
        'active_page': 'dashboard',
    }

    return render(request, 'student/dashboard.html', context)


# =========================
# STUDENT PROFILE
# =========================
@login_required
def student_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name')
        profile.department = request.POST.get('department')
        profile.save()

    return render(request, 'student/profile.html', {
        'profile': profile,
        'active_page': 'profile'
    })


@login_required
def edit_student_profile(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.email = request.POST.get('email')
        request.user.save()
        return redirect('student_profile')

    return render(request, 'student/edit_profile.html')


# =========================
# AVAILABLE EXAMS
# =========================
@login_required
def available_exams(request):
    exams = Exam.objects.filter(status='active')

    return render(request, 'student/available_exams.html', {
        'exams': exams,
        'active_page': 'exams'
    })


# =========================
# EXAM HISTORY
# =========================
@login_required
def exam_history(request):
    student = request.user.profile
    attempts = ExamAttempt.objects.filter(student=student)

    return render(request, 'student/exam_history.html', {
        'attempts': attempts,
        'active_page': 'history'
    })


# =========================
# EXAM RESULT (STATIC FOR NOW)
# =========================
@login_required
def exam_result(request):
    return render(request, 'student/result.html', {
        'active_page': 'history'
    })


# =========================
# START EXAM
# =========================
@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, status='active')
    student = request.user.profile

    # Prevent multiple attempts
    attempt, created = ExamAttempt.objects.get_or_create(
        student=student,
        exam=exam
    )

    if created:
        for question in exam.questions.all():
            StudentAnswer.objects.create(
                attempt=attempt,
                question=question
            )

    return redirect('exam_attempt', attempt_id=attempt.id)


# =========================
# EXAM ATTEMPT (QUESTIONS PAGE)
# =========================
@login_required
def exam_attempt(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    exam = attempt.exam
    questions = exam.questions.all().order_by('id')

    return render(request, 'student/exam_attempt.html', {
        'attempt': attempt,
        'exam': exam,
        'questions': questions,
        'active_page': 'exams'
    })

from django.contrib import messages

@login_required
def submit_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user.profile)

    if request.method == 'POST':
        answers = StudentAnswer.objects.filter(attempt=attempt)
        score = 0

        for ans in answers:
            selected = request.POST.get(f"q{ans.question.id}")
            if selected:
                ans.selected_answer = selected
                if selected == ans.question.correct_answer:
                    score += ans.question.marks
                ans.save()

        attempt.score = score
        attempt.is_submitted = True
        attempt.status = 'completed'

        # PASS / FAIL logic (50% default)
        pass_mark = attempt.exam.total_marks * 0.5
        attempt.result = 'PASS' if score >= pass_mark else 'FAIL'

        attempt.save()
    if attempt.is_submitted:
        messages.success(request, "✅ Exam submitted successfully!")
        return redirect('exam_history')
