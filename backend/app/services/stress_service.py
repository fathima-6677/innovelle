import boto3
import json
from app.core.config import settings

class StressInferenceService:
    def get_stress_score(self, hr_variability: float, motion_intensity: float, time_of_day: str) -> tuple[int, str]:
        """Call SageMaker Random Forest model or fallback to a deterministic mock score"""
        if settings.MOCK_AWS or settings.KMS_KEY_ID == "mockKmsKeyId":
            return self._calculate_mock_score(hr_variability, motion_intensity)

        try:
            sagemaker_client = boto3.client("sagemaker-runtime", region_name=settings.AWS_DEFAULT_REGION)
            payload = {
                "hr_variability": hr_variability,
                "motion_intensity": motion_intensity,
                "time_of_day": time_of_day
            }
            # Invoke SageMaker Endpoint
            response = sagemaker_client.invoke_endpoint(
                EndpointName="autiguard-stress-classifier",
                ContentType="application/json",
                Body=json.dumps(payload)
            )
            result = json.loads(response["Body"].read().decode())
            return result.get("stress_index", 50), result.get("risk_level", "NORMAL")
        except Exception as e:
            print(f"SageMaker inference call failed, using mock engine: {e}")
            return self._calculate_mock_score(hr_variability, motion_intensity)

    def classify_distress_audio(self, audio_embedding: list[float]) -> tuple[bool, float]:
        """Classify if audio embedding represents screams/distress (CNN classifier proxy)"""
        # Simulated classifer on audio embeddings
        if settings.MOCK_AWS or settings.KMS_KEY_ID == "mockKmsKeyId":
            # Deterministic simulation: average embedding score
            avg_val = sum(audio_embedding) / len(audio_embedding) if audio_embedding else 0
            is_distress = avg_val > 0.75
            confidence = avg_val
            return is_distress, confidence

        try:
            sagemaker_client = boto3.client("sagemaker-runtime", region_name=settings.AWS_DEFAULT_REGION)
            response = sagemaker_client.invoke_endpoint(
                EndpointName="autiguard-distress-audio-classifier",
                ContentType="application/json",
                Body=json.dumps({"embedding": audio_embedding})
            )
            result = json.loads(response["Body"].read().decode())
            return result.get("is_distress", False), result.get("confidence", 0.0)
        except Exception as e:
            print(f"SageMaker audio inference failed: {e}")
            return False, 0.0

    def _calculate_mock_score(self, hrv: float, motion: float) -> tuple[int, str]:
        # High motion + low HRV = high stress
        # Let's map HRV (normally 20-100 ms) and motion (0-10 m/s^2)
        base = 30
        if hrv < 40:
            base += 30
        if motion > 6.0:
            base += 30
        
        # Clamp to 0-100
        score = min(max(base, 0), 100)
        if score >= 75:
            risk = "SEVERE"
        elif score >= 50:
            risk = "ELEVATED"
        else:
            risk = "NORMAL"
        return int(score), risk

stress_service = StressInferenceService()
