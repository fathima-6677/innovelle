from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from app.core.security import get_current_user
from app.core.config import settings
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

# Note on Rate Limiter:
# To use slowapi limiter without circular imports (from app.main import limiter),
# you should ideally define the limiter in a separate file (e.g., app/core/limiter.py).
# We omit the _get_limiter() local import hack here to avoid issues and clarify that
# the @limiter.limit() decorator was missing.

@router.post("/login")
def login(request: Request, payload: LoginRequest):
    """
    Authenticate via mock or real Cognito pool and return signed local token.
    """
    # Debug logs as requested
    print("LOGIN CALLED")
    print(f"Email: {payload.email}")
    print(f"MOCK_AWS = {settings.MOCK_AWS}")

    # MOCK MODE
    if settings.MOCK_AWS:
        if payload.email == "error@autiguard.org":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password."
            )

        # Generate a properly signed JWT using settings.JWT_SECRET
        local_demo_jwt = jwt.encode(
            {
                "email": payload.email,
                "role": "org_admin" if "admin" in payload.email else "caregiver",
                "org_id": "ORG#demo-org-99",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            settings.JWT_SECRET,
            algorithm="HS256"
        )

        return {
            "access_token": local_demo_jwt,
            "token_type": "bearer",
            "role": "org_admin" if "admin" in payload.email else "caregiver",
            "name": "Demo User",
            "org_id": "ORG#demo-org-99"
        }

    # AWS COGNITO MODE
    import boto3
    from botocore.exceptions import ClientError

    try:
        client = boto3.client(
            "cognito-idp",
            region_name=settings.AWS_DEFAULT_REGION
        )

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

        if not id_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed."
            )

        # Decode the token without verification just to extract user attributes
        decoded = jwt.decode(
            id_token,
            options={"verify_signature": False}
        )

        return {
            "access_token": id_token,
            "token_type": "bearer",
            "role": decoded.get("custom:role", "caregiver"),
            "name": decoded.get("name", "Demo User"),
            "org_id": decoded.get("custom:org_id", "ORG#demo-org-99")
        }

    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.response["Error"]["Message"]
        )

    except Exception as e:
        # Corrected Indentation
        print("LOGIN ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/signup")
def signup(payload: SignupRequest):
    """Create caregiver or org account inside Cognito"""
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


# ── Caregiver Settings ────────────────────────────────────────────────────────

class SettingsPayload(BaseModel):
    escalationMinutes: int = 5
    primaryPhone: str
    secondaryPhone: str
    enableWhatsapp: bool = True
    enableMfa: bool = False

@router.post("/settings")
def save_settings(payload: SettingsPayload, current_user: dict = Depends(get_current_user)):
    """Persist caregiver notification and security settings"""
    from app.core.dynamodb import db
    user_email = current_user.get("email", "unknown@autiguard.org")

    settings_item = {
        "PK": f"USER#{user_email}",
        "SK": "SETTINGS",
        "escalation_minutes": payload.escalationMinutes,
        "primary_phone": payload.primaryPhone,
        "secondary_phone": payload.secondaryPhone,
        "enable_whatsapp": payload.enableWhatsapp,
        "enable_mfa": payload.enableMfa,
    }
    db.put_item(settings_item)

    return {
        "status": "success",
        "message": "Settings saved successfully.",
        "email": user_email
    }


@router.get("/settings")
def get_settings(current_user: dict = Depends(get_current_user)):
    """Retrieve saved caregiver settings"""
    from app.core.dynamodb import db
    user_email = current_user.get("email", "unknown@autiguard.org")
    item = db.get_item(f"USER#{user_email}", "SETTINGS")
    if not item:
        return {}   # Return empty dict — frontend will use localStorage defaults
    return {
        "escalationMinutes": item.get("escalation_minutes", 5),
        "primaryPhone": item.get("primary_phone", ""),
        "secondaryPhone": item.get("secondary_phone", ""),
        "enableWhatsapp": item.get("enable_whatsapp", True),
        "enableMfa": item.get("enable_mfa", False),
    }


# ── Team Member Management ────────────────────────────────────────────────────

@router.delete("/users/{email}")
def delete_user(email: str, current_user: dict = Depends(get_current_user)):
    """Remove a team member from the organization (Cognito + DB)"""
    from app.core.config import settings as app_settings
    import boto3
    from botocore.exceptions import ClientError

    if not app_settings.MOCK_AWS:
        try:
            client = boto3.client("cognito-idp", region_name=app_settings.AWS_DEFAULT_REGION)
            client.admin_delete_user(
                UserPoolId=app_settings.COGNITO_USER_POOL_ID,
                Username=email
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.response["Error"]["Message"]
            )

    return {
        "status": "success",
        "message": f"User {email} removed from organization."
    }

