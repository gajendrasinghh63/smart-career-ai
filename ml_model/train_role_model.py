

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# Correct path because command root folder se run hota hai
data = pd.read_csv("dataset/role_data.csv")

X = data[[
    "cgpa",
    "technical",
    "communication",
    "aptitude",
    "projects",
    "internships"
]]

y = data["role"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

pred = model.predict(X_test)
accuracy = accuracy_score(y_test, pred)

print("Role model trained successfully")
print("Accuracy:", round(accuracy * 100, 2), "%")

joblib.dump(model, "ml_model/role_model.pkl")
print("Role model saved successfully")