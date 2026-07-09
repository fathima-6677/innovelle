import pytest
from fastapi.testclient import TestClient
import os

# Set environment before loading the app
os.environ["DYNAMODB_TABLE"] = "AutiGuardCoreTest"
os.environ["MOCK_AWS"] = "True"
os.environ["KMS_KEY_ID"] = "mockKmsKeyId"
os.environ["COGNITO_USER_POOL_ID"] = "ap-south-1_mockPoolId"

from app.main import app
from app.core.dynamodb import db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes the DynamoDB Local or Mock table for testing"""
    try:
        # Create test table if using DynamoDB Local
        db.client.create_table(
            TableName="AutiGuardCoreTest",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "STRING"},
                {"AttributeName": "SK", "AttributeType": "STRING"},
                {"AttributeName": "GSI1PK", "AttributeType": "STRING"},
                {"AttributeName": "GSI1SK", "AttributeType": "STRING"}
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        print("✅ Test DynamoDB Table Created successfully.")
    except Exception as e:
        print(f"Test DynamoDB Table init warning: {e} (Assuming mock mode or table already exists)")
    
    yield
    
    try:
        db.client.delete_table(TableName="AutiGuardCoreTest")
        print("✅ Test DynamoDB Table Cleared.")
    except Exception:
        pass

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    # Helper to generate mock auth headers
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImN1c3RvbTtyb2xlIjoiY2FyZWdpdmVyIiwib3JnX2lkIjoiT1JHI2RlbW8tb3JnLTk5IiwiZW1haWwiOiJjYXJlZ2l2ZXJAYXV0aWd1YXJkLm9yZyJ9.signature"
    return {"Authorization": f"Bearer {token}"}
