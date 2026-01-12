from django.db import models
from django.conf import settings

class Exam(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=200)
    faculty = models.ForeignKey(
        'accounts.Profile',
        on_delete=models.CASCADE,
        related_name='exams'
    )
    subject = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    total_marks = models.IntegerField(default=0)
    duration = models.IntegerField(help_text="Minutes")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    allowed_departments = models.CharField(max_length=200)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_answer = models.CharField(
        max_length=1,
        choices=[('A','A'),('B','B'),('C','C'),('D','D')]
    )

    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.text[:50]

    class Meta:
        ordering = ['id']


class ExamAttempt(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    student = models.ForeignKey(
        'accounts.Profile',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    violations = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, default='Completed')
    created_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(
        max_length=10,
        choices=[('PASS', 'PASS'), ('FAIL', 'FAIL')],
        blank=True,
        null=True
    )
    def __str__(self):
        return f"{self.student.full_name} - {self.exam.title}"

class StudentAnswer(models.Model):
    attempt = models.ForeignKey('ExamAttempt', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        unique_together = ('attempt', 'question')
