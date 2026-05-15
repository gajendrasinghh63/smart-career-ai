
from django.contrib import admin
from .models import StudentProfile, PredictionResult


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'college_name', 'branch', 'cgpa', 'resume_score']
    search_fields = ['full_name', 'email', 'college_name', 'branch']


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'prediction', 'probability', 'suggested_role', 'created_at']
    search_fields = ['student__full_name', 'prediction', 'suggested_role']