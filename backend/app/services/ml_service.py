import joblib
import logging
import os
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.model = None
        # Locate the model file. Since this runs in backend/app/services, we need to go up to Athidh/ml
        # Base dir is likely E:/Athidh/backend, so the ML dir is E:/Athidh/ml
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.model_path = base_dir / "ml" / "autiguard_random_forest.pkl"

    def load_model(self):
        try:
            if not self.model_path.exists():
                logger.warning(f"ML Model not found at {self.model_path}. ML predictions will be disabled.")
                return
            
            logger.info(f"Loading ML model from {self.model_path}...")
            self.model = joblib.load(str(self.model_path))
            logger.info("ML model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self.model = None

    def predict_stress(self, heart_rate: float, accel_magnitude: float = 9.8, temperature: float = 36.5) -> int:
        """
        Predict stress score based on features.
        The random forest model typically expects specific features.
        We provide fallbacks if some sensor data is not available.
        """
        if self.model is None:
            return None

        try:
            # Assuming the model was trained on ['HeartRate', 'AccelMagnitude', 'Temperature']
            # Adjust these feature names/order based on actual model requirements if known.
            # We'll use a pandas DataFrame to pass named features just in case.
            features = pd.DataFrame([{
                'HeartRate': heart_rate,
                'AccelMagnitude': accel_magnitude,
                'Temperature': temperature
            }])
            
            prediction = self.model.predict(features)
            # Ensure the output is an integer bounded between 0 and 100
            score = int(prediction[0])
            return max(0, min(100, score))
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return None

ml_service = MLService()
