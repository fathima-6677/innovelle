from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import jwt
import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str
    phone: str | None = None
    role: str = "caregiver"  # caregiver, org_admin, super_admin

@router.post("/login")
def login(payload: LoginRequest):
    """Authenticate via mock or real Cognito pool and return signed local token"""
    from app.core.config import settings
    import boto3
    from botocore.exceptions import ClientError

    if not settings.MOCK_AWS:
        try:
            client = boto3.client("cognito-idp", region_name=settings.AWS_DEFAULT_REGION)
            response = client.initiate_auth(
                ClientId=settings.COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": payload.email,
                    "PASSWORD": payload.password
                }
            )
            auth_result = response.get("AuthenticationResult", {})
            id_token = auth_result.get("IdToken")
            
            # Decode claims to retrieve role and organization id
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            role = decoded.get("custom:role", "caregiver")
            name = decoded.get("name", "Demo User")
            org_id = decoded.get("custom:org_id", "ORG#demo-org-99")
            
            return {
                "access_token": id_token,
                "token_type": "bearer",
                "role": role,
                "name": name,
                "org_id": org_id
            }
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.response["Error"]["Message"]
            )

    if payload.email == "error@autiguard.org":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password."
        )

    # For local/mock development, we sign a local JWT token.
    token_claims = {
        "sub": "user-uuid-123456",
        "email": payload.email,
        "custom:role": "org_admin" if "admin" in payload.email else "caregiver",
        "org_id": "ORG#demo-org-99",
        "name": "Demo User",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    encoded_jwt = jwt.encode(token_claims, "localSecretKey", algorithm="HS256")
    
    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "role": token_claims["custom:role"],
        "name": token_claims["name"],
        "org_id": token_claims["org_id"]
    }

@router.post("/signup")
def signup(payload: SignupRequest):
    """Create caregiver or org account inside Cognito"""
    from app.core.config import settings
    import boto3
    from botocore.exceptions import ClientError

    if not settings.MOCK_AWS:
        try:
            client = boto3.client("cognito-idp", region_name=settings.AWS_DEFAULT_REGION)
            user_attributes = [
                {"Name": "email", "Value": payload.email},
                {"Name": "custom:role", "Value": payload.role},
                {"Name": "name", "Value": payload.name}
            ]
            if payload.phone:
                user_attributes.append({"Name": "phone_number", "Value": payload.phone})

            response = client.sign_up(
                ClientId=settings.COGNITO_CLIENT_ID,
                Username=payload.email,
                Password=payload.password,
                UserAttributes=user_attributes
            )
            return {
                "status": "success",
                "message": "User registration successfully initiated. Verification email sent.",
                "email": payload.email,
                "role": payload.role,
                "user_sub": response.get("UserSub")
            }
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.response["Error"]["Message"]
            )

    # Simulated Cognito Sign-up success
    return {
        "status": "success",
        "message": "User registration successfully initiated. Verification email sent.",
        "email": payload.email,
        "role": payload.role
    }
