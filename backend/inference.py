import joblib
import pandas as pd

model = joblib.load("../ml/autiguard_random_forest.pkl")

sample = pd.DataFrame([{
    "heart_rate": 120,
    "acc_x": 0.2,
    "acc_y": 0.3,
    "acc_z": 0.4,
    "acceleration_magnitude": 1.2,
    "sound_level": 75,
    "time_of_day": 11
}])

prediction = model.predict(sample)
confidence = model.predict_proba(sample)

print("Prediction:", prediction)
print("Confidence:", confidence)