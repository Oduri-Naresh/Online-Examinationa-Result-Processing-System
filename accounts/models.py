from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )

    DEPT_CHOICES = (
        ('CSE', 'CSE'),
        ('ECE', 'ECE'),
        ('EEE', 'EEE'),
        ('IT', 'IT'),
        ('MECH', 'MECH'),
    )

    YEAR_CHOICES = (
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
    )

    APPROVAL_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    # ================= CORE =================
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    full_name = models.CharField(max_length=150)
    email = models.EmailField()

    department = models.CharField(
        max_length=10,
        choices=DEPT_CHOICES,
        null=True,
        blank=True
    )

    # ================= STUDENT =================
    student_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    year = models.CharField(
        max_length=1,
        choices=YEAR_CHOICES,
        null=True,
        blank=True
    )

    # ================= FACULTY APPROVAL =================
    approval_status = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default='Pending'
    )

    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_faculties'
    )




    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    @property
    def is_approved(self):
        return self.approval_status == "Approved"
