import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DYNAMODB_TABLE: str = "AutiGuardCore"
    DYNAMODB_ENDPOINT: str | None = None  # None for real DynamoDB, http://localhost:8000 for local

    AWS_DEFAULT_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None

    COGNITO_USER_POOL_ID: str = "ap-south-1_mockPoolId"
    COGNITO_CLIENT_ID: str = "mockClientId"
    COGNITO_JWKS_URL: str | None = None

    KMS_KEY_ID: str = "mockKmsKeyId"
    
    # Flags for testing/mocking
    MOCK_AWS: bool = True
    LOCAL_ENCRYPTION_KEY: str = "XsXwWhAuOK8-KAgQ598H5VlUGVwiuCP2WKpFsEZTOpk="
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Twilio (fully dispatched or mocked)
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"
    TWILIO_WHATSAPP_TO: str = "whatsapp:+919629455996"
    TWILIO_TEMPLATE_SID: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
