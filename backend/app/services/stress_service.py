import boto3
import json
import joblib
import pandas as pd

from app.core.config import settings


class StressInferenceService:

    def __init__(self):
        # Load model once during startup
        self.model = joblib.load("../ml/autiguard_random_forest.pkl")

    def get_stress_score(
        self,
        hr_variability: float,
        motion_intensity: float,
        time_of_day: str
    ) -> tuple[float, str]:

        # LOCAL DEVELOPMENT (MOCK_AWS=True)
        if settings.MOCK_AWS or settings.KMS_KEY_ID == "mockKmsKeyId":

            sample = pd.DataFrame([{
                "heart_rate": hr_variability,
                "acc_x": 0,
                "acc_y": 0,
                "acc_z": 0,
                "acceleration_magnitude": motion_intensity,
                "sound_level": 0,
                "time_of_day": int(time_of_day)
            }])

            prediction = self.model.predict(sample)[0]

            confidence = max(
                self.model.predict_proba(sample)[0]
            )

            labels = {
                0: "SAFE",
                1: "STRESS",
                2: "DANGER"
            }

            return round(confidence * 100, 2), labels[prediction]

        # PRODUCTION (SageMaker)
        try:
            sagemaker_client = boto3.client(
                "sagemaker-runtime",
                region_name=settings.AWS_DEFAULT_REGION
            )

            payload = {
                "hr_variability": hr_variability,
                "motion_intensity": motion_intensity,
                "time_of_day": time_of_day
            }

            response = sagemaker_client.invoke_endpoint(
                EndpointName="autiguard-stress-classifier",
                ContentType="application/json",
                Body=json.dumps(payload)
            )

            result = json.loads(
                response["Body"].read().decode()
            )

            return (
                result.get("stress_index", 50),
                result.get("risk_level", "NORMAL")
            )

        except Exception as e:
            print(
                f"SageMaker inference failed: {e}"
            )

            return 0.0, "UNKNOWN"

    def classify_distress_audio(
        self,
        audio_embedding: list[float]
    ) -> tuple[bool, float]:

        # Keep this as-is until CNN is built
        if settings.MOCK_AWS or settings.KMS_KEY_ID == "mockKmsKeyId":

            avg_val = (
                sum(audio_embedding) / len(audio_embedding)
                if audio_embedding
                else 0
            )

            is_distress = avg_val > 0.75
            confidence = avg_val

            return is_distress, confidence

        try:

            sagemaker_client = boto3.client(
                "sagemaker-runtime",
                region_name=settings.AWS_DEFAULT_REGION
            )

            response = sagemaker_client.invoke_endpoint(
                EndpointName="autiguard-distress-audio-classifier",
                ContentType="application/json",
                Body=json.dumps({
                    "embedding": audio_embedding
                })
            )

            result = json.loads(
                response["Body"].read().decode()
            )

            return (
                result.get("is_distress", False),
                result.get("confidence", 0.0)
            )

        except Exception as e:

            print(
                f"SageMaker audio inference failed: {e}"
            )

            return False, 0.0


stress_service = StressInferenceService()
