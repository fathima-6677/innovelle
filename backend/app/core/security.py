import base64
import jwt
import requests
import json
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.fernet import Fernet
from app.core.config import settings
import boto3

security_bearer = HTTPBearer()

# Standard KMS/Local Cryptography key setup for mock/real cases
# For mock purposes, we load a persistent Fernet key from configuration.
encryption_key = settings.LOCAL_ENCRYPTION_KEY.encode()
cipher = Fernet(encryption_key)

# 1. KMS Field-Level Encryption / Decryption Wrapper
def encrypt_field(text: str) -> str:
    """Encrypt PII field using KMS or fallback to local Fernet cipher if MOCK_AWS=True"""
    if not text:
        return ""
    if settings.MOCK_AWS or settings.KMS_KEY_ID == "mockKmsKeyId":
        return cipher.encrypt(text.encode()).decode()
    
    try:
        kms_client = boto3.client("kms", region_name=settings.AWS_DEFAULT_REGION)
        response = kms_client.encrypt(
            KeyId=settings.KMS_KEY_ID,
            Plaintext=text.encode('utf-8')
        )
        return base64.b64encode(response['CiphertextBlob']).decode('utf-8')
    except Exception as e:
        print(f"KMS encryption failed, falling back: {e}")
        return cipher.encrypt(text.encode()).decode()

def decrypt_field(cipher_text: str) -> str:
    """Decrypt PII field using KMS or fallback to local Fernet cipher if MOCK_AWS=True"""
    if not cipher_text:
        return ""
    try:
        if settings.MOCK_AWS or settings.KMS_KEY_ID == "mockKmsKeyId":
            return cipher.decrypt(cipher_text.encode()).decode()
        
        kms_client = boto3.client("kms", region_name=settings.AWS_DEFAULT_REGION)
        raw_bytes = base64.b64decode(cipher_text.encode('utf-8'))
        response = kms_client.decrypt(
            CiphertextBlob=raw_bytes
        )
        return response['Plaintext'].decode('utf-8')
    except Exception as e:
        print(f"KMS decryption failed: {e}")
        try:
            return cipher.decrypt(cipher_text.encode()).decode()
        except Exception:
            return "[Decryption Error]"


# 2. Cognito JWT Authentication & RBAC Guards
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, creds: HTTPAuthorizationCredentials = Depends(security_bearer)) -> dict:
        token = creds.credentials
        
        # Local bypass for mock mode - only enabled in non-production
        if settings.MOCK_AWS and settings.ENVIRONMENT.lower() != "production":
            try:
                # First try verifying with local secret key
                decoded = jwt.decode(token, "localSecretKey", algorithms=["HS256"])
            except jwt.ExpiredSignatureError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token expired: {str(e)}"
                )
            except jwt.InvalidTokenError:
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                except jwt.InvalidTokenError as e:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid or malformed token: {str(e)}"
                    )
            
            user_role = decoded.get("custom:role", "caregiver")
            if user_role not in self.allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: insufficient permissions"
                )
            if "sub" not in decoded:
                decoded["sub"] = "mock-user-123"
            if "email" not in decoded:
                decoded["email"] = "caregiver@autiguard.org"
            if "custom:role" not in decoded:
                decoded["custom:role"] = user_role
            if "org_id" not in decoded:
                decoded["org_id"] = "ORG#demo-org-99"
            return decoded

        # Real Cognito Verification
        try:
            # Decode token header to verify against JWKS keys
            headers = jwt.get_unverified_header(token)
            kid = headers.get("kid")
            
            # Simple JWKS fetch
            jwks_url = settings.COGNITO_JWKS_URL or f"https://cognito-idp.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
            jwks = requests.get(jwks_url).json()
            
            key_data = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    key_data = key
                    break
                    
            if not key_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token kid")
                
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_data))
            decoded = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=settings.COGNITO_CLIENT_ID
            )
            
            # Cognito puts groups in 'cognito:groups' or custom attributes
            user_role = decoded.get("custom:role") or (decoded.get("cognito:groups", ["caregiver"])[0] if decoded.get("cognito:groups") else "caregiver")
            if user_role not in self.allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: insufficient permissions"
                )
            return decoded
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )

# Dependency helpers
get_current_user = RoleChecker(["super_admin", "org_admin", "caregiver"])
get_org_admin = RoleChecker(["super_admin", "org_admin"])
get_super_admin = RoleChecker(["super_admin"])

def get_optional_user(request: Request) -> dict | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed Authorization header"
        )
        
    token = parts[1]
    
    # Local bypass for mock mode - only enabled in non-production
    if settings.MOCK_AWS and settings.ENVIRONMENT.lower() != "production":
        try:
            decoded = jwt.decode(token, "localSecretKey", algorithms=["HS256"])
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token expired: {str(e)}"
            )
        except jwt.InvalidTokenError:
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
            except jwt.InvalidTokenError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid or malformed token: {str(e)}"
                )
        if "custom:role" not in decoded:
            decoded["custom:role"] = "caregiver"
        return decoded
        
    # Real Cognito Verification
    try:
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")
        
        jwks_url = settings.COGNITO_JWKS_URL or f"https://cognito-idp.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()
        
        key_data = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                key_data = key
                break
                
        if not key_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token kid")
            
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_data))
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.COGNITO_CLIENT_ID
        )
        return decoded
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )
