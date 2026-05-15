from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    college_name = models.CharField(max_length=150)
    branch = models.CharField(max_length=100)
    semester = models.IntegerField()
    cgpa = models.FloatField()
    attendance = models.FloatField()
    communication_skill = models.IntegerField()
    technical_skill = models.IntegerField()
    aptitude_skill = models.IntegerField()
    projects_count = models.IntegerField()
    internships_count = models.IntegerField()
    certifications_count = models.IntegerField()
    resume_score = models.FloatField(default=0)

    # 🔥 NEW FIELD (IMPORTANT)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    def __str__(self):
        return self.full_name


class PredictionResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    prediction = models.CharField(max_length=50)
    probability = models.FloatField()
    suggested_role = models.CharField(max_length=100)
    missing_skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.prediction}"