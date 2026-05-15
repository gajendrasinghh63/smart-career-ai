

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


data = pd.read_csv("dataset/placement_data.csv")

X = data[
    [
        "cgpa",
        "attendance",
        "communication_skill",
        "technical_skill",
        "aptitude_skill",
        "projects_count",
        "internships_count",
        "certifications_count",
        "resume_score",
    ]
]

y = data["placed"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=6,
    min_samples_split=3,
    min_samples_leaf=1,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("Model trained successfully")
print("Accuracy:", round(accuracy * 100, 2), "%")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred))

joblib.dump(model, "ml_model/model.pkl")

print("Model saved successfully")