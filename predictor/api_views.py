from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import joblib
import pandas as pd


# Load trained ML model
placement_model = joblib.load("ml_model/model.pkl")


@api_view(["GET", "POST"])
def predict_api(request):
    # GET = API status check
    if request.method == "GET":
        return Response({
            "success": True,
            "message": "Smart Career AI API is running successfully ✅",
            "method": "Use POST request for placement prediction",
            "required_fields": [
                "cgpa",
                "attendance",
                "communication",
                "technical",
                "aptitude",
                "projects",
                "internships",
                "certifications",
                "resume_score"
            ]
        })

    try:
        data = request.data

        cgpa = float(data.get("cgpa", 7))
        attendance = float(data.get("attendance", 75))
        communication = float(data.get("communication", 60))
        technical = float(data.get("technical", 60))
        aptitude = float(data.get("aptitude", 60))
        projects = int(data.get("projects", 1))
        internships = int(data.get("internships", 0))
        certifications = int(data.get("certifications", 0))
        resume_score = float(data.get("resume_score", 50))

        # Basic validation
        if not (0 <= cgpa <= 10):
            return Response({
                "success": False,
                "error": "CGPA must be between 0 and 10"
            }, status=status.HTTP_400_BAD_REQUEST)

        for field_name, value in {
            "attendance": attendance,
            "communication": communication,
            "technical": technical,
            "aptitude": aptitude,
            "resume_score": resume_score
        }.items():
            if not (0 <= value <= 100):
                return Response({
                    "success": False,
                    "error": f"{field_name} must be between 0 and 100"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Use DataFrame to avoid sklearn feature-name warning
        input_data = pd.DataFrame([{
            "cgpa": cgpa,
            "attendance": attendance,
            "communication_skill": communication,
            "technical_skill": technical,
            "aptitude_skill": aptitude,
            "projects_count": projects,
            "internships_count": internships,
            "certifications_count": certifications,
            "resume_score": resume_score
        }])

        prediction = placement_model.predict(input_data)[0]
        probability_raw = placement_model.predict_proba(input_data)[0][1]

        placement_status = "Placed" if prediction == 1 else "Not Placed"
        probability = round(min(probability_raw * 100, 95), 2)

        return Response({
            "success": True,
            "input": {
                "cgpa": cgpa,
                "attendance": attendance,
                "communication": communication,
                "technical": technical,
                "aptitude": aptitude,
                "projects": projects,
                "internships": internships,
                "certifications": certifications,
                "resume_score": resume_score
            },
            "prediction": {
                "status": placement_status,
                "probability": probability
            }
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            "success": False,
            "error": "Invalid input. Please send numeric values only."
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)