from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets

app = FastAPI(title="TTS Authentication API")

# JWT configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security
security = HTTPBearer(auto_error=False)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock user databases
USERS = {"admin": "admin123", "demo": "demo123", "user": "password"}

EMAIL_USERS = {
    "admin@namisense.ai": "admin123",
    "user@namisense.ai": "password123",
    "demo@namisense.ai": "demo123",
}

ALLOWED_DOMAIN = "namisense.ai"


# Pydantic models
class LoginRequest(BaseModel):
    identifier: str
    password: str


class UserResponse(BaseModel):
    username: str
    email: Optional[str] = None


class TokenResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LogoutResponse(BaseModel):
    success: bool


class SessionResponse(BaseModel):
    authenticated: bool
    user: Optional[UserResponse] = None


class HealthResponse(BaseModel):
    status: str


# Helper functions
def validate_email_domain(email: str) -> bool:
    """Validate that email belongs to allowed domain"""
    return "@" in email and email.endswith(f"@{ALLOWED_DOMAIN}")


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """Verify JWT token and return user data"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        email: Optional[str] = payload.get("email")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"username": username, "email": email}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# API endpoints
@app.post("/api/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and create JWT token.
    Accepts either username or email authentication.
    """
    identifier = request.identifier
    password = request.password

    if not identifier or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username/email and password required",
        )

    user_info = None

    # Check if identifier is an email (contains @)
    if "@" in identifier:
        # Email authentication
        if not validate_email_domain(identifier):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only {ALLOWED_DOMAIN} email addresses are allowed",
            )

        if identifier in EMAIL_USERS and EMAIL_USERS[identifier] == password:
            # Extract username from email (part before @)
            username = identifier.split("@")[0]
            user_info = {"username": username, "email": identifier}
    else:
        # Username authentication
        if identifier in USERS and USERS[identifier] == password:
            user_info = {"username": identifier, "email": None}

    if user_info:
        # Create JWT token with user data
        token_data = {"sub": user_info["username"], "email": user_info["email"]}
        access_token = create_access_token(token_data)

        return TokenResponse(
            success=True,
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user_info),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


@app.post("/api/logout", response_model=LogoutResponse)
async def logout():
    """
    Logout endpoint (client-side token deletion).
    Returns success as token management is handled by client.
    """
    return LogoutResponse(success=True)


@app.get("/api/session", response_model=SessionResponse)
@app.get("/api/verify", response_model=SessionResponse)
async def verify_session(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """
    Verify JWT token and return authentication status.
    Returns user info if authenticated, otherwise returns not authenticated.
    """
    if credentials is None:
        return SessionResponse(authenticated=False, user=None)

    try:
        user_data = verify_token(credentials)
        return SessionResponse(
            authenticated=True,
            user=UserResponse(**user_data),
        )
    except HTTPException:
        return SessionResponse(authenticated=False, user=None)


@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="ok")


if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("FastAPI Authentication Server Starting")
    print("=" * 50)
    print("\nDemo Credentials (Username/Password):")
    print("  Username: admin | Password: admin123")
    print("  Username: demo  | Password: demo123")
    print("  Username: user  | Password: password")
    print("\nDemo Credentials (Email/Password - @namisense.ai only):")
    print("  Email: admin@namisense.ai | Password: admin123")
    print("  Email: user@namisense.ai  | Password: password123")
    print("  Email: demo@namisense.ai  | Password: demo123")
    print("\nServer running on http://localhost:5000")
    print("API Documentation: http://localhost:5000/docs")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=5000)
