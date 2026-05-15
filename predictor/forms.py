from django import forms


class SmartPredictionForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    target_role = forms.ChoiceField(
        choices=[
            ("python developer", "Python Developer"),
            ("data analyst", "Data Analyst"),
            ("web developer", "Web Developer"),
            ("tester", "Tester"),
        ],
        required=False
    )

    phone = forms.CharField(max_length=15, required=False)
    college_name = forms.CharField(max_length=150, required=False)
    branch = forms.CharField(max_length=100, required=False)
    semester = forms.IntegerField(required=False)
    cgpa = forms.FloatField(required=False)
    attendance = forms.FloatField(required=False)
    communication_skill = forms.IntegerField(required=False)
    technical_skill = forms.IntegerField(required=False)
    aptitude_skill = forms.IntegerField(required=False)
    projects_count = forms.IntegerField(required=False)
    internships_count = forms.IntegerField(required=False)
    certifications_count = forms.IntegerField(required=False)
    resume_score = forms.FloatField(required=False)

    resume = forms.FileField(required=False)