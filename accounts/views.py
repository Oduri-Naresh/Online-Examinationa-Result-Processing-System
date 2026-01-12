# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from .decorators import admin_required
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.db import models
from exams_app.models import Exam, ExamAttempt
from .models import Profile

def home(request):
    return render(request, 'home.html')



# ================= STUDENT REGISTRATION =================

def student_register(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        student_id = request.POST.get('student_id')
        department = request.POST.get('department')
        year = request.POST.get('year')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # ---------- VALIDATIONS ----------

        if User.objects.filter(username=username).exists():
            return render(request, 'student/register.html', {
                'error': 'Username already exists'
            })

        if Profile.objects.filter(student_id=student_id).exists():
            return render(request, 'student/register.html', {
                'error': 'Student ID already registered'
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'student/register.html', {
                'error': 'Email already registered'
            })

        # ---------- CREATE USER ----------
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=full_name
        )

        # ---------- CREATE STUDENT PROFILE ----------
        Profile.objects.create(
            user=user,
            role='student',
            full_name=full_name,
            email=email,
            student_id=student_id,
            department=department,
            year=year
        )

        return redirect('student_login')

    return render(request, 'student/register.html')

# ================= FACULTY REGISTRATION =================
def faculty_register(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        department = request.POST.get('department')

        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Password match check
        if password != confirm_password:
            return render(request, 'faculty/register.html', {
                'error': 'Passwords do not match'
            })

        # Username validation
        if User.objects.filter(username=username).exists():
            return render(request, 'faculty/register.html', {
                'error': 'Username already exists'
            })

        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=full_name
        )

        # Create Faculty Profile (Pending Approval)
        Profile.objects.create(
            user=user,
            full_name=full_name,
            role='faculty',
            email=email,
            department=department,
            approval_status='Pending'
        )

        return redirect('faculty_login')

    return render(request, 'faculty/register.html')

def student_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, 'student/login.html', {
                'error': 'Invalid username or password'
            })

        try:
            profile = Profile.objects.get(user=user, role='student')
        except Profile.DoesNotExist:
            return render(request, 'student/login.html', {
                'error': 'This account is not a student account'
            })

        # ✅ SUCCESS
        login(request, user)
        return redirect('student_dashboard')

    return render(request, 'student/login.html')

def faculty_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect("faculty_login")

        # ✅ Get profile safely
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            messages.error(request, "Faculty profile not found")
            return redirect("faculty_login")

        # ✅ ROLE CHECK (FIXED)
        if profile.role != "faculty":
            messages.error(request, "You are not authorized as Faculty")
            return redirect("faculty_login")

        # 🔒 ADMIN APPROVAL CHECK
        if profile.approval_status == "Pending":
            messages.warning(
                request,
                "⏳ Waiting for admin approval. Please try again later."
            )
            return redirect("faculty_login")

        if profile.approval_status == "Rejected":
            messages.error(
                request,
                "❌ Your registration was rejected by admin."
            )
            return redirect("faculty_login")

        # ✅ SUCCESS LOGIN
        login(request, user)
        return redirect("faculty_dashboard")

    return render(request, "faculty/login.html")

from .decorators import student_required


@login_required
def faculty_dashboard(request):
    faculty = request.user.profile

    total_exams = Exam.objects.filter(faculty=faculty).count()
    active_exams = Exam.objects.filter(faculty=faculty).count()
    completed_exams = Exam.objects.filter(faculty=faculty).count()

    avg_pass = 0  # calculate later if needed

    return render(request, 'faculty/dashboard.html', {
        'total_exams': total_exams,
        'active_exams': active_exams,
        'completed_exams': completed_exams,
        'avg_pass': avg_pass,
    })


@login_required
def faculty_exams(request):
    # get faculty profile
    faculty_profile = get_object_or_404(
        Profile,
        user=request.user,
        role='faculty'
    )

    # filter exams using Profile (✅ correct)
    exams = Exam.objects.filter(faculty=faculty_profile)

    total_exams = exams.count()

    # ❌ REMOVE status filter (you don't have status field)
    active_exams = exams.count()   # temporary safe logic

    # calculate avg pass %
    attempts = ExamAttempt.objects.filter(exam__in=exams)
    passed = attempts.filter(passed=True).count()
    total_attempts = attempts.count()

    avg_pass = int((passed / total_attempts) * 100) if total_attempts > 0 else 0

    return render(request, 'faculty/exam.html', {
        'exams': exams,
        'total_exams': total_exams,
        'active_exams': active_exams,
        'avg_pass': avg_pass
    })

@login_required
def faculty_students(request):
    students = Profile.objects.filter(role='student')

    student_data = []
    for s in students:
        attempts = ExamAttempt.objects.filter(student=s)

        avg_pass = 0
        if attempts.exists():
            avg_pass = attempts.filter(is_pass=True).count() * 100 / attempts.count()

        student_data.append({
            'student': s,
            'avg_pass': round(avg_pass, 2)
        })

    return render(request, 'faculty/student.html', {
        'student_data': student_data
    })
@login_required
def faculty_student_detail(request, student_id):
    student = get_object_or_404(Profile, id=student_id, role='student')

    attempts = ExamAttempt.objects.filter(student=student)

    passed_count = attempts.filter(passed=True).count()
    failed_count = attempts.filter(passed=False).count()

    avg_score = attempts.aggregate(avg=Avg('score'))['avg'] or 0

    return render(request, 'faculty/student_detail.html', {
        'student': student,
        'attempts': attempts,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'avg_score': round(avg_score, 2),
    })
@login_required
def faculty_delete_student(request, student_id):
    student = get_object_or_404(Profile, id=student_id, role='student')

    if request.method == 'POST':
        student.user.delete()  # deletes auth user safely
        student.delete()

    return redirect('faculty_students')


def faculty_profile(request):
    profile, created = Profile.objects.get_or_create(
    user=request.user,
    defaults={
        "full_name": request.user.username,
        "approval_status": "approved"
    }
)


@login_required
def add_exam(request):
    if request.method == 'POST':

        mode = request.POST.get('mode')  # ai / manual

        exam = Exam.objects.create(
            title=request.POST.get('title'),
            subject=request.POST.get('subject'),
            description=request.POST.get('description'),
            total_marks=request.POST.get('total_marks'),
            duration=request.POST.get('duration'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            allowed_departments=request.POST.get('departments'),
            faculty=request.user.profile
        )

        # 🔹 AI GENERATED EXAM
        if mode == 'ai':
            generate_ai_questions(exam)
            return redirect('faculty_exams')

        # 🔹 MANUAL EXAM
        return redirect('add_exam_questions', exam_id=exam.id)

    return render(request, 'faculty/add_exam.html')

from exams_app.models import Question

def generate_ai_questions(exam):
    sample_questions = [
        ("What is Python?", "Programming Language"),
        ("What is Django?", "Web Framework"),
        ("What is ORM?", "Object Relational Mapping"),
    ]

    for q, a in sample_questions:
        Question.objects.create(
            exam=exam,
            question_text=q,
            correct_answer=a,
            marks=5
        )

def add_exam_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam)
    if request.method == 'POST':

        # ✅ Get & clean data
        text = request.POST.get('question_text', '').strip()
        option_a = request.POST.get('option_a', '').strip()
        option_b = request.POST.get('option_b', '').strip()
        option_c = request.POST.get('option_c', '').strip()
        option_d = request.POST.get('option_d', '').strip()
        correct_answer = request.POST.get('correct_answer')
        marks = request.POST.get('marks')

        # 🚨 VALIDATION (MOST IMPORTANT)
        if not text:
            messages.error(request, "Question text cannot be empty.")
            return redirect('add_exam_questions', exam_id=exam.id)

        if not all([option_a, option_b, option_c, option_d]):
            messages.error(request, "All options are required.")
            return redirect('add_exam_questions', exam_id=exam.id)

        if correct_answer not in ['A', 'B', 'C', 'D']:
            messages.error(request, "Select a valid correct answer.")
            return redirect('add_exam_questions', exam_id=exam.id)

        if not marks:
            messages.error(request, "Marks are required.")
            return redirect('add_exam_questions', exam_id=exam.id)

        # ✅ SAVE QUESTION
        Question.objects.create(
            exam=exam,
            text=text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            marks=int(marks)
        )

        messages.success(request, "Question added successfully!")

        # ➕ Add another question
        if 'add_another' in request.POST:
            return redirect('add_exam_questions', exam_id=exam.id)

        # ✅ Finish exam
        if 'finish_exam' in request.POST:
            exam.status = 'completed'
            exam.save()
            return redirect('faculty_exams')

    return render(request, 'faculty/add_questions.html', {
        'exam': exam,
        'questions': questions
    })
def faculty_profile(request):
    profile = request.user.profile
    return render(request, 'faculty/profile.html', {'profile': profile})


def edit_faculty_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        profile.full_name = request.POST.get('full_name')
        profile.email = request.POST.get('email')
        profile.department = request.POST.get('department')
        profile.save()

        return redirect('faculty_profile')

    return render(request, 'faculty/edit_profile.html', {'profile': profile})

def edit_exam_question(request, exam_id, question_id):
    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id, exam=exam)

    if request.method == 'POST':
        question.text = request.POST.get('question_text')
        question.option_a = request.POST.get('option_a')
        question.option_b = request.POST.get('option_b')
        question.option_c = request.POST.get('option_c')
        question.option_d = request.POST.get('option_d')
        question.correct_answer = request.POST.get('correct_answer')
        question.marks = request.POST.get('marks')
        question.save()
        update_exam_total_marks(exam)
        return redirect('add_exam_questions', exam_id=exam.id)

    return render(request, 'faculty/edit_question.html', {
        'exam': exam,
        'question': question
    })

def delete_exam_question(request, exam_id, question_id):
    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id, exam=exam)
    question.delete()

    update_exam_total_marks(exam)
    return redirect('add_exam_questions', exam_id=exam.id)

def update_exam_total_marks(exam):
    total = exam.questions.aggregate(
        total=models.Sum('marks')
    )['total'] or 0

    exam.total_marks = total
    exam.save()
    
def faculty_start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, faculty=request.user.profile)
    exam.status = 'active'
    exam.save()
    return redirect('faculty_exams')


def stop_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam.status = 'completed'
    exam.save()
    return redirect('faculty_exams')

def monitor_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    attempts = ExamAttempt.objects.filter(exam=exam)

    return render(request, 'faculty/monitor_exam.html', {
        'exam': exam,
        'attempts': attempts
    })

def force_submit(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    attempt.is_submitted = True
    attempt.save()
    return redirect('monitor_exam', exam_id=attempt.exam.id)

def preview_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()

    return render(request, 'faculty/preview_exam.html', {
        'exam': exam,
        'questions': questions
    })

from exams_app.models import Exam, ExamAttempt
from django.db.models import Count

@login_required
def exam_results(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    attempts = ExamAttempt.objects.filter(
        exam=exam,
        is_submitted=True
    ).select_related('student__user')

    total_attempted = attempts.count()
    passed = attempts.filter(result='PASS').count()
    failed = attempts.filter(result='FAIL').count()

    pass_percentage = (
        (passed / total_attempted) * 100
        if total_attempted > 0 else 0
    )

    context = {
        'exam': exam,
        'attempts': attempts,
        'total_attempted': total_attempted,
        'passed': passed,
        'failed': failed,
        'pass_percentage': round(pass_percentage, 2),
    }

    return render(request, 'faculty/exam_results.html', context)

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from accounts.models import Profile
from exams_app.models import ExamAttempt


def download_students_pdf(request):
    students = Profile.objects.filter(role='student')

    student_data = []

    for student in students:
        attempts = ExamAttempt.objects.filter(student=student, is_submitted=True)

        total = attempts.count()
        passed = attempts.filter(passed=True).count()

        avg_pass = int((passed / total) * 100) if total > 0 else 0

        student_data.append({
            'student': student,
            'avg_pass': avg_pass
        })

    template = get_template('faculty/student_pdf.html')
    html = template.render({'student_data': student_data})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="students.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response


@staff_member_required
def faculty_approval_dashboard(request):
    pending_faculties = Profile.objects.filter(
        role='faculty',
        approval_status='Pending'
    )

    return render(request, 'admin/faculty_approval.html', {
        'pending_faculties': pending_faculties
    })


@staff_member_required
def approve_faculty(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, role='faculty')
    profile.approval_status = 'Approved'
    profile.approved_by = request.user
    profile.save()
    return redirect('faculty_approval')


@staff_member_required
def reject_faculty(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, role='faculty')
    profile.approval_status = 'Rejected'
    profile.approved_by = request.user
    profile.save()
    return redirect('faculty_approval')

def admin_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user and user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid admin credentials")

    return render(request, "admin/login.html")


def admin_required(view_func):
    return login_required(
        user_passes_test(lambda u: u.is_superuser)(view_func)
    )

@admin_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')

    students_count = Profile.objects.filter(role='student').count()
    faculty_count = Profile.objects.filter(role='faculty').count()
    pending_count = Profile.objects.filter(
        role='faculty',
        approval_status='Pending'
    ).count()

    pending_faculty = Profile.objects.filter(
        role='faculty',
        approval_status='Pending'
    )

    context = {
        'students_count': students_count,
        'faculty_count': faculty_count,
        'pending_count': pending_count,
        'pending_faculty': pending_faculty,
    }

    return render(request, 'admin/dashboard.html', context)
@login_required
def approve_faculty(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    profile.approval_status = 'Approved'
    profile.approved_by = request.user
    profile.save()

    messages.success(request, "✅ Faculty approved successfully")
    return redirect('admin_dashboard')


@login_required
def reject_faculty(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    profile.approval_status = 'Rejected'
    profile.approved_by = request.user
    profile.save()

    messages.error(request, "❌ Faculty rejected")
    return redirect('admin_dashboard')
from reportlab.pdfgen import canvas
from django.http import HttpResponse

@login_required



def user_logout(request):
    logout(request)
    return redirect("home")