from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage

import joblib
import numpy as np
import PyPDF2
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .forms import SmartPredictionForm
from .models import StudentProfile, PredictionResult


placement_model = joblib.load("ml_model/model.pkl")


ROLE_SKILLS = {
    "Python Developer": ["python", "django", "sql", "git"],
    "Java Developer": ["java", "sql", "spring"],
    "Web Developer": ["html", "css", "javascript", "django"],
    "Frontend Developer": ["html", "css", "javascript", "react", "bootstrap"],
    "Backend Developer": ["python", "django", "sql", "api"],
    "Full Stack Developer": ["html", "css", "javascript", "react", "python", "django", "sql"],
    "Data Analyst": ["python", "sql", "excel", "power bi", "data analysis"],
    "Data Scientist": ["python", "machine learning", "pandas", "numpy", "data analysis"],
    "AI Engineer": ["python", "machine learning", "numpy", "pandas"],
    "Machine Learning Engineer": ["python", "machine learning", "scikit-learn", "numpy", "pandas"],
    "Software Engineer": ["python", "java", "c++", "sql", "git"],
    "Tester": ["testing", "manual testing", "automation testing"],
    "QA Engineer": ["testing", "automation testing", "selenium"],
    "DevOps Engineer": ["git", "linux", "docker", "aws"],
    "Cyber Security Analyst": ["network security", "linux", "python"],
    "Database Administrator": ["sql", "database", "mysql"],
    "UI UX Designer": ["figma", "ui", "ux"],
    "Mobile App Developer": ["java", "kotlin", "android"],
    "Cloud Engineer": ["aws", "cloud", "linux"],
    "Support Engineer": ["communication", "troubleshooting", "sql"],
}


def extract_skills(file):
    text = ""

    try:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception:
        return []

    text = text.lower()

    skills_db = [
        "python", "java", "c++", "html", "css", "javascript",
        "sql", "django", "react", "machine learning",
        "data analysis", "excel", "power bi", "git",
        "api", "bootstrap", "numpy", "pandas",
        "testing", "manual testing", "automation testing",
        "spring", "scikit-learn", "selenium", "linux",
        "docker", "aws", "network security", "database",
        "mysql", "figma", "ui", "ux", "kotlin",
        "android", "cloud", "communication", "troubleshooting"
    ]

    return [skill for skill in skills_db if skill in text]


def estimate(skills):
    count = len(skills)

    return {
        "cgpa": min(8.8, 6.5 + count * 0.2),
        "attendance": min(95, 70 + count * 2),
        "communication": min(90, 50 + count * 3),
        "technical": min(95, 50 + count * 4),
        "aptitude": min(90, 50 + count * 2),
        "projects": max(1, count // 2),
        "internships": 1 if count > 4 else 0,
        "resume_score": min(100, count * 10),
    }


def predict_placement(student):
    data = np.array([[
        student.cgpa,
        student.attendance,
        student.communication_skill,
        student.technical_skill,
        student.aptitude_skill,
        student.projects_count,
        student.internships_count,
        student.certifications_count,
        student.resume_score
    ]])

    pred = placement_model.predict(data)[0]
    prob = placement_model.predict_proba(data)[0][1]

    status = "Placed" if pred == 1 else "Not Placed"
    probability = round(min(prob * 100, 95), 2)

    return status, probability


def dynamic_role_from_skills(skills):
    best_role = "General Career Role"
    best_score = 0

    for role, required_skills in ROLE_SKILLS.items():
        matched = [skill for skill in required_skills if skill in skills]
        score = len(matched) / len(required_skills)

        if score > best_score:
            best_score = score
            best_role = role

    return best_role


def get_missing_skills(role, skills):
    required = ROLE_SKILLS.get(role, [])
    return [skill for skill in required if skill not in skills]


def get_suggestions(student, skills, role):
    suggestions = []

    missing = get_missing_skills(role, skills)

    if missing:
        suggestions.append("Learn role-specific missing skills: " + ", ".join(missing))

    if student.projects_count < 2:
        suggestions.append("Add at least 2 strong projects related to your target role.")

    if student.internships_count < 1:
        suggestions.append("Complete one internship or real-world project experience.")

    if student.communication_skill < 70:
        suggestions.append("Improve communication and interview skills.")

    if student.resume_score < 70:
        suggestions.append("Improve resume quality by adding achievements and project details.")

    if not suggestions:
        suggestions.append("Profile looks strong. Keep practicing interviews and DSA.")

    return suggestions


def explain_prediction(student, prediction, probability, role, skills):
    skill_text = ", ".join(skills[:6]) if skills else "limited detected skills"

    if prediction == "Placed":
        return (
            f"The system predicted Placed because the resume contains relevant skills like {skill_text}. "
            f"The technical score, resume score, and profile strength support the suggested role: {role}."
        )

    return (
        "The system predicted Not Placed because the profile needs improvement in technical skills, "
        "projects, internship experience, communication, or resume quality."
    )


def get_score_breakdown(student):
    return {
        "CGPA Score": round(student.cgpa * 10, 2),
        "Technical Skill": student.technical_skill,
        "Communication": student.communication_skill,
        "Aptitude": student.aptitude_skill,
        "Resume Score": student.resume_score,
        "Projects Score": min(student.projects_count * 20, 100),
        "Internship Score": min(student.internships_count * 30, 100),
    }


def generate_pdf_buffer(student, result):
    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 55

    def line(text, size=11, bold=False, gap=22):
        nonlocal y

        if y < 80:
            p.showPage()
            y = height - 55

        p.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        p.drawString(55, y, str(text)[:95])
        y -= gap

    line("Smart Career AI Report", 18, True, 35)
    line(f"Student Name: {student.full_name}")
    line(f"Email: {student.email}")
    line(f"Placement Status: {result.prediction}")
    line(f"Probability: {result.probability}%")
    line(f"Suggested Role: {result.suggested_role}", 11, False, 30)

    line("Detected Skills:", 13, True)

    skills_text = result.missing_skills or "No skills detected"
    parts = [skills_text[i:i + 90] for i in range(0, len(skills_text), 90)]

    for part in parts:
        line(part, 10, False, 18)

    line("", 5, False, 10)
    line("Improvement Note:", 13, True)
    line("Improve missing role skills, add strong projects, and practice interviews.", 10)
    line("This report was generated using resume analysis and ML prediction.", 10)

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer


def send_report_email(student, result):
    pdf_buffer = generate_pdf_buffer(student, result)

    email = EmailMessage(
        subject="Smart Career AI Prediction Report",
        body=f"""
Hello {student.full_name},

Your Smart Career AI report has been generated.

Placement Status: {result.prediction}
Probability: {result.probability}%
Suggested Role: {result.suggested_role}

Please find your PDF report attached.

Regards,
Smart Career AI
""",
        from_email="smartcareerai@example.com",
        to=[student.email],
    )

    email.attach(
        f"{student.full_name}_career_report.pdf",
        pdf_buffer.getvalue(),
        "application/pdf"
    )

    email.send()


@login_required
def home_view(request):
    form = SmartPredictionForm(request.POST or None, request.FILES or None)

    prediction = None
    probability = None
    remaining_probability = 100
    role = None
    skills = []
    suggestions = []
    explanation = None
    missing_skills = []
    score_data = {}

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        resume = data.get("resume")

        if not resume:
            messages.error(request, "Please upload a resume PDF first.")
        else:
            skills = extract_skills(resume)
            estimated = estimate(skills)

            student, created = StudentProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    "full_name": data["full_name"],
                    "email": data["email"],
                    "phone": data.get("phone") or "",
                    "college_name": data.get("college_name") or "",
                    "branch": data.get("branch") or "General",
                    "semester": data.get("semester") or 6,
                    "cgpa": estimated.get("cgpa", 7),
                    "attendance": estimated.get("attendance", 75),
                    "communication_skill": estimated.get("communication", 60),
                    "technical_skill": estimated.get("technical", 60),
                    "aptitude_skill": estimated.get("aptitude", 60),
                    "projects_count": estimated.get("projects", 1),
                    "internships_count": estimated.get("internships", 0),
                    "certifications_count": data.get("certifications_count") or 0,
                    "resume_score": estimated.get("resume_score", 50),
                    "resume": resume
                }
            )

            if not created:
                student.full_name = data["full_name"]
                student.email = data["email"]
                student.cgpa = estimated.get("cgpa", student.cgpa)
                student.attendance = estimated.get("attendance", student.attendance)
                student.communication_skill = estimated.get("communication", student.communication_skill)
                student.technical_skill = estimated.get("technical", student.technical_skill)
                student.aptitude_skill = estimated.get("aptitude", student.aptitude_skill)
                student.projects_count = estimated.get("projects", student.projects_count)
                student.internships_count = estimated.get("internships", student.internships_count)
                student.resume_score = estimated.get("resume_score", student.resume_score)
                student.resume = resume
                student.save()

            prediction, probability = predict_placement(student)
            remaining_probability = round(100 - probability, 2)

            role = dynamic_role_from_skills(skills)
            missing_skills = get_missing_skills(role, skills)
            suggestions = get_suggestions(student, skills, role)
            explanation = explain_prediction(student, prediction, probability, role, skills)
            score_data = get_score_breakdown(student)

            result = PredictionResult.objects.create(
                student=student,
                prediction=prediction,
                probability=probability,
                suggested_role=role,
                missing_skills=", ".join(skills)
            )

            send_report_email(student, result)
            messages.success(request, "Prediction completed and report email generated successfully.")

    query = request.GET.get("q", "")

    results = PredictionResult.objects.all().order_by("-id")

    if query:
        results = (
            results.filter(student__full_name__icontains=query)
            | results.filter(prediction__icontains=query)
            | results.filter(suggested_role__icontains=query)
        )

    all_results = PredictionResult.objects.all()
    total = all_results.count()
    placed_count = all_results.filter(prediction="Placed").count()
    not_placed_count = all_results.filter(prediction="Not Placed").count()

    return render(request, "predictor/home.html", {
        "form": form,
        "prediction": prediction,
        "probability": probability,
        "remaining_probability": remaining_probability,
        "role": role,
        "skills": skills,
        "suggestions": suggestions,
        "explanation": explanation,
        "missing_skills": missing_skills,
        "score_data": score_data,
        "results": results,
        "total": total,
        "placed_count": placed_count,
        "not_placed_count": not_placed_count,
        "query": query,
    })


@login_required
def clear_history(request):
    if request.method == "POST":
        PredictionResult.objects.all().delete()
        messages.success(request, "Prediction history cleared successfully.")

    return redirect("home")


@login_required
def download_pdf(request, id):
    result = get_object_or_404(PredictionResult, id=id)
    student = result.student

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{student.full_name}_career_report.pdf"'

    pdf_buffer = generate_pdf_buffer(student, result)
    response.write(pdf_buffer.getvalue())

    return response