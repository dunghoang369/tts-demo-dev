from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    status,
    Request,
    UploadFile,
    File,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import os
import re
import httpx
import firebase_admin
from firebase_admin import credentials, firestore
import logging
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TTS Authentication API")

# External API Configuration
GET_NEWS_API_URL = "http://115.79.192.192:19977/get_news"
GET_NEWS_CATEGORY_API_URL = "http://115.79.192.192:19977/get_news_type"
SUMMARIZE_API_URL = "http://115.79.192.192:19977/summarize"
TTS_API_KEY = "zNBVyiatKn5eTvC2CEvDg1msgOCHrTZ55zZ0qfsu"
NEWS_CATEGORIES = ["thoi-su", "the-gioi", "kinh-doanh", "the-thao"]
CRAWL_INTERVAL_HOURS = int(os.getenv("CRAWL_INTERVAL_HOURS", "6"))

# JWT configuration - use environment variable in production
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "fallback-development-key-change-in-production"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security
security = HTTPBearer(auto_error=False)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Truncate password to 72 bytes for bcrypt
    if plain_password == hashed_password:
        return True
    return False


def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    try:
        # Truncate password to 72 bytes for bcrypt
        if len(password.encode("utf-8")) > 72:
            password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise


# CORS configuration - allow all origins for flexible deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock user databases with role-based access control
USERS = {
    "namitech_standard": {"password": "LT3kzk46e5Q6bqmK", "role": "standard"},
    "namitech_pro": {"password": "LT3kzk46e5Q6bqmM", "role": "pro"},
    "namitech": {"password": "LT3kzk46e5Q6bqmK", "role": "premium"},
}

EMAIL_USERS = {
    "standard@namisense.ai": {"password": "standard123", "role": "standard"},
    "pro@namisense.ai": {"password": "pro123", "role": "pro"},
    "premium@namisense.ai": {"password": "premium123", "role": "premium"},
}

ALLOWED_DOMAIN = os.getenv("ALLOWED_DOMAIN", "namisense.ai")

# Firebase initialization
_firebase_initialized = False
_db = None


def init_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_initialized, _db
    if _firebase_initialized:
        return _db

    try:
        # Check if Firebase app is already initialized
        try:
            # If already initialized, just get the client
            _db = firestore.client()
            _firebase_initialized = True
            logger.info("Firebase already initialized, using existing app")
            return _db
        except ValueError:
            # Not initialized yet, proceed with initialization
            pass

        # Option 1: Try to load credentials from environment variable
        firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

        if firebase_creds_json:
            # Parse JSON from environment variable
            import json

            cred_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
            _firebase_initialized = True
            logger.info("Firebase initialized successfully using environment variable")
            return _db

        # Option 2: Fall back to file-based credentials (for local development)
        possible_paths = [
            "firebase-credentials.json",  # Current directory
            "../firebase-credentials.json",  # Parent directory (when running from api/)
            os.path.join(
                os.path.dirname(__file__), "..", "firebase-credentials.json"
            ),  # Relative to this file
        ]

        cred_path = None
        for path in possible_paths:
            if os.path.exists(path):
                cred_path = path
                break

        if not cred_path:
            raise FileNotFoundError(
                "Firebase credentials not found. Set FIREBASE_CREDENTIALS_JSON environment variable or place firebase-credentials.json file."
            )

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        _firebase_initialized = True
        logger.info(f"Firebase initialized successfully using {cred_path}")
        return _db
    except Exception as e:
        logger.error(f"Error initializing Firebase: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return None


async def migrate_users_to_firestore():
    """One-time migration of hardcoded users to Firestore"""
    db = init_firebase()
    if not db:
        logger.error("Cannot migrate users: Firebase not initialized")
        return False

    try:
        logger.info("Starting user migration to Firestore...")
        auth_collection = db.collection("authentication")
        migrated_count = 0

        # Migrate USERS (username-based)
        for username, data in USERS.items():
            try:
                doc_ref = auth_collection.document(username)
                doc_ref.set(
                    {
                        "username": username,
                        "email": None,
                        "password": get_password_hash(data["password"]),
                        "role": data["role"],
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "last_login": None,
                        "is_active": True,
                    }
                )
                migrated_count += 1
                logger.info(f"Migrated user: {username}")
            except Exception as e:
                logger.error(f"Error migrating user {username}: {e}")

        # Migrate EMAIL_USERS (email-based)
        for email, data in EMAIL_USERS.items():
            try:
                username = email.split("@")[0]  # Use email prefix as username
                doc_ref = auth_collection.document(f"email_{username}")
                doc_ref.set(
                    {
                        "username": username,
                        "email": email,
                        "password": get_password_hash(data["password"]),
                        "role": data["role"],
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "last_login": None,
                        "is_active": True,
                    }
                )
                migrated_count += 1
                logger.info(f"Migrated email user: {email}")
            except Exception as e:
                logger.error(f"Error migrating email user {email}: {e}")

        logger.info(f"Successfully migrated {migrated_count} users to Firestore")
        return True
    except Exception as e:
        logger.error(f"Error migrating users: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return False


async def get_user_from_firestore(username: str = None, email: str = None):
    """Get user from Firestore by username or email"""
    db = init_firebase()
    if not db:
        return None

    try:
        auth_collection = db.collection("authentication")

        if email:
            # Query by email
            query = (
                auth_collection.where("email", "==", email)
                .where("is_active", "==", True)
                .limit(1)
            )
            docs = query.stream()
            for doc in docs:
                return doc.to_dict()
        elif username:
            # Query by username or document ID
            doc_ref = auth_collection.document(username)
            doc = doc_ref.get()
            if doc.exists:
                user_data = doc.to_dict()
                if user_data.get("is_active", True):
                    return user_data

            # Also try email_{username} format
            doc_ref = auth_collection.document(f"email_{username}")
            doc = doc_ref.get()
            if doc.exists:
                user_data = doc.to_dict()
                if user_data.get("is_active", True):
                    return user_data

        return None
    except Exception as e:
        logger.error(f"Error fetching user from Firestore: {e}")
        return None


async def update_last_login(username: str = None, email: str = None):
    """Update user's last login timestamp"""
    db = init_firebase()
    if not db:
        return

    try:
        auth_collection = db.collection("authentication")

        if email:
            query = auth_collection.where("email", "==", email).limit(1)
            docs = query.stream()
            for doc in docs:
                doc.reference.update(
                    {"last_login": datetime.now(timezone.utc).isoformat()}
                )
                return
        elif username:
            # Try both username formats
            for doc_id in [username, f"email_{username}"]:
                doc_ref = auth_collection.document(doc_id)
                if doc_ref.get().exists:
                    doc_ref.update(
                        {"last_login": datetime.now(timezone.utc).isoformat()}
                    )
                    return
    except Exception as e:
        logger.error(f"Error updating last login: {e}")


async def get_news_category():
    """Get available news categories from the API"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(
            GET_NEWS_CATEGORY_API_URL,
            headers={
                "accept": "application/json",
                "api-key": TTS_API_KEY,
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()


async def get_news(news_type: str, limit: int = 5):
    """Fetch news from the external API"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            GET_NEWS_API_URL,
            headers={
                "accept": "application/json",
                "api-key": TTS_API_KEY,
                "Content-Type": "application/json",
            },
            json={"news_type": news_type, "limit": limit},
        )
        response.raise_for_status()
        return response.json()


async def summarize_text(full_text: str):
    """Call the summarization API to get a summary of the text"""
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                SUMMARIZE_API_URL,
                headers={
                    "accept": "application/json",
                    "api-key": TTS_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"content": full_text},
            )
            response.raise_for_status()
            result = response.json()

            if result.get("status") == 0 and "summary" in result:
                return result["summary"]
            else:
                logger.warning(f"API returned non-zero status: {result}")
                return None
    except Exception as e:
        logger.error(f"Error calling summarize API: {e}")
        return None


async def generate_tts_audio(content: str, voice_id: int = 4, sample_rate: int = 22050):
    """
    Generate TTS audio from text content
    Args:
        content: Text to synthesize
        voice_id: Voice ID (4 = Hồng Phượng)
        sample_rate: Audio quality (22050 = High Quality)
    Returns:
        base64 encoded audio string or None if failed
    """
    try:
        API_URL = "http://115.79.192.192:19977/invocations"
        API_KEY = "zNBVyiatKn5eTvC2CEvDg1msgOCHrTZ55zZ0qfsu"

        request_body = {
            "content": content,
            "rate": 1.0,
            "sample_rate": sample_rate,
            "accent": voice_id,
            "return_type": "url",
            "audio_format": "wav",
            "max_word_per_sent": 100,
            "is_summary": 1,
        }

        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                API_URL,
                json=request_body,
                headers={
                    "accept": "application/json",
                    "api-key": API_KEY,
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("audio")  # base64 encoded audio
            else:
                logger.error(f"TTS API error: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"Error generating TTS audio: {e}")
        return None


def upload_to_firestore(db, news_items: List[dict], fetch_metadata: dict):
    """Upload news items to Firestore collection with metadata"""
    try:
        collection_ref = db.collection("news_articles")

        # Store metadata document
        metadata_doc = {
            "fetch_date": fetch_metadata.get("fetch_date", datetime.now().isoformat()),
            "total_items": len(news_items),
            "news_type": fetch_metadata.get("news_type", "multiple"),
            "timestamp": firestore.SERVER_TIMESTAMP,
            "last_crawl_time": datetime.now().isoformat(),
        }

        # Add metadata document
        collection_ref.document("_metadata").set(metadata_doc, merge=True)

        # Upload each news item
        uploaded_count = 0
        for item in news_items:
            # Generate doc ID from timestamp and title hash
            doc_id = f"{item['publish_time']}_{hash(item['title']) % 10000}"
            collection_ref.document(doc_id).set(item)
            uploaded_count += 1

        logger.info(f"Successfully uploaded {uploaded_count} items to Firestore")
        return uploaded_count
    except Exception as e:
        logger.error(f"Error uploading to Firestore: {e}")
        return 0


async def process_and_upload_news(news_type: str, limit: int = 5):
    """
    Process news for a specific category:
    1. Fetch 10 news articles from API
    2. Filter articles with full_text > 50 characters
    3. Keep only the first 5 filtered articles
    4. Summarize each article
    5. Upload to Firestore
    Returns: dict with processing statistics
    """
    try:
        # Get category mapping
        news_category = await get_news_category()
        category = news_category.get(news_type, {}).get("category", news_type)

        # Fetch 10 news articles
        news = await get_news(news_type, 10)
        results = news.get("results", {})
        articles = results.get("articles", [])

        if not articles:
            logger.warning(f"No articles found for category: {news_type}")
            return {
                "category": category,
                "articles": 0,
                "uploaded": 0,
                "failed": 0,
            }

        # Filter articles with full_text > 50 characters
        filtered_articles = [
            article for article in articles if len(article.get("full_text", "")) > 50
        ]

        logger.info(
            f"Fetched {len(articles)} articles, {len(filtered_articles)} passed filter (full_text > 50)"
        )

        # Keep only the first 5 filtered articles
        articles_to_process = filtered_articles[:5]
        logger.info(f"Processing {len(articles_to_process)} articles")

        if not articles_to_process:
            logger.warning(f"No articles passed the filter for category: {news_type}")
            return {
                "category": category,
                "articles": len(articles),
                "uploaded": 0,
                "failed": 0,
            }

        news_items = []
        fetch_date = datetime.now().isoformat()
        failed_count = 0

        for article in articles_to_process:
            try:
                title = article.get("title", "")
                publish_datetime = article.get("publish_time", "")
                full_text = article.get("full_text", "")
                url = article.get("url", "")

                # Extract and parse date/time using regex
                date_match = re.search(r"(\d{2})/(\d{2})/(\d{4})", publish_datetime)
                publish_date = (
                    f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"
                    if date_match
                    else ""
                )

                time_match = re.search(r"(\d{2}):(\d{2})", publish_datetime)
                publish_time_str = (
                    f"{time_match.group(1)}:{time_match.group(2)}"
                    if time_match
                    else "00:00"
                )

                # Convert to timestamp
                if publish_date and publish_time_str:
                    try:
                        date_time = datetime.strptime(
                            f"{publish_date} {publish_time_str}", "%Y-%m-%d %H:%M"
                        )
                        timestamp = int(date_time.timestamp())
                    except ValueError:
                        logger.warning(
                            f"Failed to parse date: {publish_date} {publish_time_str}"
                        )
                        timestamp = int(datetime.now().timestamp())
                else:
                    timestamp = int(datetime.now().timestamp())

                # Summarize the article
                summary = await summarize_text(full_text)

                if not summary:
                    logger.warning(f"Failed to summarize: {title[:50]}...")
                    failed_count += 1
                    continue

                item = {
                    "title": title,
                    "full_text": full_text,
                    "summary": summary,
                    "publish_time": timestamp,
                    "url": url,
                    "category": category,
                    "fetch_date": fetch_date,
                }

                news_items.append(item)
                logger.info(f"Processed: {title[:50]}...")

            except Exception as e:
                logger.error(f"Error processing article: {e}")
                failed_count += 1
                continue

        # Upload to Firestore
        db = init_firebase()
        if not db:
            raise Exception("Failed to initialize Firebase")

        metadata = {"fetch_date": fetch_date, "news_type": news_type}
        uploaded_count = upload_to_firestore(db, news_items, metadata)

        # Merge summaries
        merged_content = ""
        for article in news_items:
            title = article.get("title", "")
            summary = article.get("summary", "")
            if title and summary:
                merged_content += f"- {title}: {summary}\n\n"

        # Generate TTS audio for merged content
        audio_base64 = None
        if merged_content:
            logger.info(
                f"Generating TTS audio for {category} ({len(merged_content)} chars)"
            )
            audio_base64 = await generate_tts_audio(merged_content, voice_id=4)
            if audio_base64:
                logger.info(f"TTS audio generated successfully for {category}")

                # Save audio to Firestore
                try:
                    audio_doc = {
                        "category": category,
                        "content": merged_content,
                        "audio_base64": audio_base64,
                        "generated_at": datetime.now().isoformat(),
                        "voice": "Hồng Phượng",
                        "voice_id": 4,
                        "fetch_date": fetch_date,
                    }
                    db.collection("tts_audio").document(
                        f"{category}_{int(datetime.now().timestamp())}"
                    ).set(audio_doc)
                    logger.info(f"TTS audio saved to Firestore for {category}")
                except Exception as e:
                    logger.error(f"Error saving TTS audio to Firestore: {e}")
            else:
                logger.warning(f"Failed to generate TTS audio for {category}")

        return {
            "category": category,
            "articles": len(articles),
            "uploaded": uploaded_count,
            "failed": failed_count,
            "has_audio": audio_base64 is not None,
            "audio_generated": bool(audio_base64),
        }

    except Exception as e:
        logger.error(f"Error processing news for {news_type}: {e}")
        return {
            "category": news_type,
            "articles": 0,
            "uploaded": 0,
            "failed": 0,
            "error": str(e),
        }


# Pydantic models
class LoginRequest(BaseModel):
    identifier: str
    password: str


class UserResponse(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "standard"  # Default role


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


class CrawlNewsRequest(BaseModel):
    categories: Optional[List[str]] = None
    limit: Optional[int] = 5


class CrawlNewsResponse(BaseModel):
    success: bool
    processed: int
    categories_processed: List[str]
    fetch_date: str
    details: List[dict]


# Helper functions
def get_most_recent_article_time(articles_dict):
    """Extract the most recent publish_time from articles"""
    max_time = None
    for category_data in articles_dict.values():
        for date_group in category_data.values():
            for article in date_group:
                if article.get("publish_time"):
                    if max_time is None or article["publish_time"] > max_time:
                        max_time = article["publish_time"]

    # Convert timestamp to ISO format
    if max_time:
        return datetime.fromtimestamp(max_time).isoformat()
    return datetime.now().isoformat()  # Last resort fallback


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
        role: str = payload.get("role", "standard")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"username": username, "email": email, "role": role}
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
    Now uses Firestore for user data.
    """
    identifier = request.identifier
    password = request.password

    if not identifier or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username/email and password required",
        )

    # Fetch user from Firestore
    user_data = None
    if "@" in identifier:
        # Email login - validate domain first
        if not validate_email_domain(identifier):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only {ALLOWED_DOMAIN} email addresses are allowed",
            )
        user_data = await get_user_from_firestore(email=identifier)
    else:
        # Username login
        user_data = await get_user_from_firestore(username=identifier)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Verify password
    if not verify_password(password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Update last login
    await update_last_login(
        username=user_data.get("username"), email=user_data.get("email")
    )

    # Create user info for response
    user_info = {
        "username": user_data["username"],
        "email": user_data.get("email"),
        "role": user_data["role"],
    }

    # Create JWT token with user data including role
    token_data = {
        "sub": user_info["username"],
        "email": user_info["email"],
        "role": user_info["role"],
    }
    access_token = create_access_token(token_data)

    return TokenResponse(
        success=True,
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user_info),
    )


@app.post("/api/logout", response_model=LogoutResponse)
async def logout():
    """
    Logout endpoint (client-side token deletion).
    Returns success as token management is handled by client.
    """
    return LogoutResponse(success=True)


@app.post("/api/admin/migrate-users")
async def admin_migrate_users():
    """Admin endpoint to migrate hardcoded users to Firestore (one-time use)"""
    success = await migrate_users_to_firestore()
    if success:
        return {"message": "Users migrated successfully", "status": "success"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to migrate users",
        )


@app.get("/api/admin/list-users")
async def admin_list_users():
    """Admin endpoint to list users from Firestore"""
    db = init_firebase()
    if not db:
        return {"error": "Firebase not initialized", "users": []}

    try:
        auth_collection = db.collection("authentication")
        docs = auth_collection.stream()

        users = []
        for doc in docs:
            data = doc.to_dict()
            users.append(
                {
                    "id": doc.id,
                    "username": data.get("username"),
                    "email": data.get("email"),
                    "role": data.get("role"),
                    "is_active": data.get("is_active"),
                }
            )

        return {"users": users, "count": len(users)}
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return {"error": str(e), "users": []}


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


@app.get("/api/test")
async def test():
    """Simple test endpoint to verify API is working"""
    return {
        "message": "API is working!",
        "environment": "production" if os.getenv("VERCEL") else "development",
        "jwt_key_set": bool(os.getenv("JWT_SECRET_KEY")),
        "allowed_domain": ALLOWED_DOMAIN,
    }


@app.post("/api/tts/synthesize")
async def tts_synthesize(request: Request):
    """Proxy TTS requests to external API to avoid mixed content issues"""
    import httpx

    try:
        # Get request body from frontend
        body = await request.json()

        # Add default is_summary parameter if not provided
        if "is_summary" not in body:
            body["is_summary"] = 1

        # Forward to external TTS API
        API_URL = "http://115.79.192.192:19977/invocations"
        API_KEY = "zNBVyiatKn5eTvC2CEvDg1msgOCHrTZ55zZ0qfsu"

        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                API_URL,
                json=body,
                headers={
                    "accept": "application/json",
                    "api-key": API_KEY,
                    "Content-Type": "application/json",
                },
            )

            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": "TTS API error", "details": response.text},
                )

            # Log the response for debugging
            response_data = response.json()
            logger.info(f"TTS API Response keys: {response_data.keys()}")
            logger.info(
                f"TTS API normed_text: {response_data.get('normed_text', 'NOT FOUND')}"
            )

            # Return the JSON response from TTS API
            return JSONResponse(content=response_data)

    except httpx.TimeoutException as e:
        logger.error(f"TTS API timeout: {e}")
        return JSONResponse(
            status_code=504,
            content={"error": "TTS API timeout", "message": "Request took too long"},
        )
    except httpx.HTTPError as e:
        logger.error(f"TTS HTTP error: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": "TTS API connection error", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"TTS proxy error: {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Proxy error",
                "message": f"{type(e).__name__}: {str(e)}",
            },
        )


@app.get("/api/get_latest_news")
async def get_latest_news():
    """
    Retrieve the 5 latest articles from Firestore and merge their summaries
    into a single Breaking News entry
    """
    try:
        # Initialize Firebase
        db = init_firebase()
        if not db:
            return JSONResponse(
                status_code=500, content={"error": "Failed to initialize Firebase"}
            )

        # Query Firestore for latest 5 articles
        collection_ref = db.collection("news_articles")
        query = collection_ref.order_by(
            "publish_time", direction=firestore.Query.DESCENDING
        ).limit(5)

        docs = query.stream()

        articles = []
        for doc in docs:
            # Skip metadata document
            if doc.id == "_metadata":
                continue

            article_data = doc.to_dict()
            articles.append(article_data)

        if not articles:
            return JSONResponse(status_code=404, content={"error": "No articles found"})

        # Get the most recent article's publish_time for the date
        most_recent_timestamp = articles[0].get("publish_time", 0)
        if most_recent_timestamp:
            date_obj = datetime.fromtimestamp(most_recent_timestamp, tz=timezone.utc)
            formatted_date = date_obj.strftime("%d/%m/%Y")
        else:
            formatted_date = datetime.now().strftime("%d/%m/%Y")

        # Merge all summaries into one string
        merged_content = ""
        for article in articles:
            title = article.get("title", "")
            summary = article.get("summary", "")
            if title and summary:
                merged_content += f"- {title}: {summary}\n\n"

        # Create the Breaking News entry
        breaking_news = {
            "date": formatted_date,
            "category": "Breaking News",
            "title": "Tổng hợp tin tức hôm nay",
            "content": merged_content.strip(),
        }

        return JSONResponse(content=breaking_news)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to retrieve news", "message": str(e)},
        )


@app.get("/api/get_news_by_categories")
async def get_news_by_categories():
    """
    Retrieve the 5 latest articles from each category in NEWS_CATEGORIES from Firestore.
    Returns separate arrays for each category.
    """
    try:
        # Initialize Firebase
        db = init_firebase()
        if not db:
            return JSONResponse(
                status_code=500, content={"error": "Failed to initialize Firebase"}
            )

        # Get category mappings
        try:
            news_category_map = await get_news_category()
        except Exception as e:
            logger.error(f"Failed to get category mappings: {e}")
            news_category_map = {}

        collection_ref = db.collection("news_articles")

        # Calculate 7 days ago timestamp
        seven_days_ago = datetime.now() - timedelta(days=7)
        seven_days_timestamp = seven_days_ago.timestamp()

        # Fetch articles from last 7 days ordered by publish_time
        query = collection_ref.order_by(
            "publish_time", direction=firestore.Query.DESCENDING
        ).limit(
            200
        )  # Get enough articles to ensure coverage across 7 days

        docs = query.stream()

        # Organize articles by category and date
        articles_by_category_and_date = {}

        for doc in docs:
            # Skip metadata document
            if doc.id == "_metadata":
                continue

            article_data = doc.to_dict()
            category = article_data.get("category", "")
            publish_time = article_data.get("publish_time", 0)
            fetch_date = article_data.get("fetch_date", "")

            if not category or not publish_time or not fetch_date:
                continue

            # Filter: only include articles from last 7 days
            if (
                datetime.fromisoformat(fetch_date)
                .replace(tzinfo=timezone.utc)
                .timestamp()
                < seven_days_timestamp
            ):
                continue

            # Format fetch_date for display (convert from ISO to DD/MM/YYYY)
            try:
                # Handle ISO format with or without timezone
                fetch_datetime = datetime.fromisoformat(
                    fetch_date.replace("Z", "+00:00")
                )
                formatted_date = fetch_datetime.strftime("%d/%m/%Y")
            except (ValueError, AttributeError):
                # Fallback to publish date if fetch_date is invalid
                date_obj = datetime.fromtimestamp(publish_time, tz=timezone.utc)
                formatted_date = date_obj.strftime("%d/%m/%Y")
                logger.warning(
                    f"Invalid fetch_date for article, using publish_time: {fetch_date}"
                )

            # Initialize nested structure
            if category not in articles_by_category_and_date:
                articles_by_category_and_date[category] = {}

            if formatted_date not in articles_by_category_and_date[category]:
                articles_by_category_and_date[category][formatted_date] = []

            # Add article
            formatted_article = {
                "title": article_data.get("title", ""),
                "summary": article_data.get("summary", ""),
                "date": formatted_date,
                "publish_time": publish_time,
                "url": article_data.get("url", ""),
            }

            articles_by_category_and_date[category][formatted_date].append(
                formatted_article
            )

        # Build result grouped by category with 7-day timeline
        # Map Vietnamese categories to English display names
        english_category_map = {
            "Thời sự": "Breaking News",
            "Thế giới": "World News",
            "Kinh doanh": "Investment News",
            "Thể thao": "Sport News",
        }

        result = {"categories": {}}

        for news_type in NEWS_CATEGORIES:
            # Get Vietnamese category name
            category_name = news_category_map.get(news_type, {}).get(
                "category", news_type
            )

            # Get English category name for display
            english_category = english_category_map.get(category_name, category_name)

            # Get articles for this category grouped by date
            dates_data = articles_by_category_and_date.get(category_name, {})

            if dates_data:
                # Sort dates in descending order (newest first)
                sorted_dates = sorted(
                    dates_data.keys(),
                    key=lambda d: datetime.strptime(d, "%d/%m/%Y"),
                    reverse=True,
                )

                # Create timeline entries for each date
                timeline_entries = []
                for date_str in sorted_dates:
                    articles = dates_data[date_str]

                    # Sort articles by publish_time (newest first) and limit to 5
                    articles = sorted(
                        articles, key=lambda a: a["publish_time"], reverse=True
                    )[:5]

                    # Merge summaries for this date (max 5 articles)
                    merged_content = ""
                    for article in articles:
                        title = article.get("title", "")
                        summary = article.get("summary", "")
                        if title and summary:
                            merged_content += f"\t{title}: {summary}\n\n"

                    # Create entry for this date
                    date_entry = {
                        "date": date_str,
                        "title": f"Tin tức {category_name} - {date_str}",
                        "content": merged_content.rstrip(),
                        "article_count": len(articles),
                    }

                    timeline_entries.append(date_entry)

                # Add to result with English category key
                result["categories"][english_category] = timeline_entries

        # Get last updated timestamp from metadata document
        try:
            metadata_doc = collection_ref.document("_metadata").get()
            if metadata_doc.exists:
                metadata = metadata_doc.to_dict()
                last_crawl = metadata.get("last_crawl_time")
                if last_crawl:
                    result["last_updated"] = last_crawl
                else:
                    # Fallback: use most recent article's publish_time
                    result["last_updated"] = get_most_recent_article_time(
                        articles_by_category_and_date
                    )
            else:
                # No metadata yet, use most recent article's publish_time
                result["last_updated"] = get_most_recent_article_time(
                    articles_by_category_and_date
                )
        except Exception as e:
            logger.error(f"Error fetching metadata: {e}")
            result["last_updated"] = get_most_recent_article_time(
                articles_by_category_and_date
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error retrieving news by categories: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to retrieve news by categories",
                "message": str(e),
            },
        )


@app.post("/api/crawl_news")
async def crawl_news(request: CrawlNewsRequest):
    """
    Crawl news from multiple categories, summarize, and upload to Firestore.
    Process synchronously and return results when complete.
    """
    try:
        categories = request.categories or NEWS_CATEGORIES
        limit = request.limit or 5

        logger.info(f"Starting news crawl for categories: {categories}, limit: {limit}")

        details = []
        total_processed = 0
        fetch_date = datetime.now().isoformat()

        # Process each category
        for category in categories:
            logger.info(f"Processing category: {category}")
            result = await process_and_upload_news(category, limit)
            details.append(result)
            total_processed += result.get("uploaded", 0)

        response = CrawlNewsResponse(
            success=True,
            processed=total_processed,
            categories_processed=categories,
            fetch_date=fetch_date,
            details=details,
        )

        logger.info(f"News crawl completed. Total processed: {total_processed}")
        return response

    except Exception as e:
        logger.error(f"Error in crawl_news endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to crawl news", "message": str(e)},
        )


@app.get("/api/cron/crawl_news")
async def cron_crawl_news():
    """
    Cron endpoint for automated news crawling.
    Called by Vercel Cron Jobs.
    """
    try:
        logger.info("Cron job triggered: crawl_news")

        details = []
        total_processed = 0
        fetch_date = datetime.now().isoformat()

        # Process each category
        for category in NEWS_CATEGORIES:
            logger.info(f"Processing category: {category}")
            result = await process_and_upload_news(category, 5)
            details.append(result)
            total_processed += result.get("uploaded", 0)

        logger.info(f"Cron crawl completed. Total processed: {total_processed}")

        return {
            "success": True,
            "processed": total_processed,
            "categories_processed": NEWS_CATEGORIES,
            "fetch_date": fetch_date,
            "details": details,
        }

    except Exception as e:
        logger.error(f"Error in cron crawl_news: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to crawl news", "message": str(e)},
        )


@app.get("/api/cron/cleanup")
async def cron_cleanup():
    """
    Cron endpoint for automated cleanup of old articles.
    Called by Vercel Cron Jobs.
    """
    try:
        logger.info("Cron job triggered: cleanup")

        db = init_firebase()
        if not db:
            raise Exception("Failed to initialize Firebase")

        collection_ref = db.collection("news_articles")
        cutoff_date = datetime.now() - timedelta(days=7)
        cutoff_timestamp = cutoff_date.timestamp()

        docs = collection_ref.where("publish_time", "<", cutoff_timestamp).stream()

        deleted_count = 0
        for doc in docs:
            if doc.id != "_metadata":
                doc.reference.delete()
                deleted_count += 1

        logger.info(f"Cleanup completed. Deleted {deleted_count} old articles")

        return {
            "success": True,
            "deleted": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in cron cleanup: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to cleanup", "message": str(e)},
        )


@app.post("/api/cleanup_old_news")
async def cleanup_old_news():
    """
    API endpoint to manually trigger cleanup of articles older than 7 days
    Returns statistics about deleted articles
    """
    try:
        db = init_firebase()
        collection_ref = db.collection("news_articles")

        # Calculate 7 days ago timestamp
        seven_days_ago = datetime.now() - timedelta(days=7)
        seven_days_timestamp = seven_days_ago.timestamp()

        logger.info(f"Starting cleanup of articles older than 7 days...")
        logger.info(f"Threshold: {seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')}")

        # Query articles older than 7 days
        query = collection_ref.order_by(
            "publish_time", direction=firestore.Query.ASCENDING
        )

        docs = query.stream()

        articles_to_delete = []
        articles_by_category = {}

        for doc in docs:
            # Skip metadata document
            if doc.id == "_metadata":
                continue

            article_data = doc.to_dict()
            publish_time = article_data.get("publish_time", 0)

            # Check if article is older than 7 days
            if publish_time < seven_days_timestamp:
                category = article_data.get("category", "Unknown")
                title = article_data.get("title", "No title")

                articles_to_delete.append(
                    {
                        "doc_id": doc.id,
                        "category": category,
                        "title": title,
                        "publish_time": publish_time,
                    }
                )

                # Group by category for summary
                if category not in articles_by_category:
                    articles_by_category[category] = 0
                articles_by_category[category] += 1

        if not articles_to_delete:
            logger.info("No articles older than 7 days found. Database is clean!")
            return JSONResponse(
                content={
                    "success": True,
                    "deleted_count": 0,
                    "message": "No articles older than 7 days found",
                    "by_category": {},
                    "threshold_date": seven_days_ago.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        # Perform deletion in batches
        deleted_count = 0
        batch_size = 500

        for i in range(0, len(articles_to_delete), batch_size):
            batch = db.batch()
            batch_articles = articles_to_delete[i : i + batch_size]

            for article in batch_articles:
                doc_ref = collection_ref.document(article["doc_id"])
                batch.delete(doc_ref)

            batch.commit()
            deleted_count += len(batch_articles)
            logger.info(f"Deleted {deleted_count}/{len(articles_to_delete)} articles")

        # Update metadata
        try:
            metadata_ref = collection_ref.document("_metadata")
            metadata_ref.update(
                {
                    "last_cleanup_time": datetime.now().isoformat(),
                    "last_cleanup_deleted": deleted_count,
                }
            )
            logger.info("Updated _metadata with cleanup information")
        except Exception as e:
            logger.warning(f"Could not update metadata: {e}")

        logger.info(
            f"Cleanup completed. Deleted {deleted_count} articles older than 7 days"
        )

        return JSONResponse(
            content={
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Successfully deleted {deleted_count} articles",
                "by_category": articles_by_category,
                "threshold_date": seven_days_ago.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    except Exception as e:
        logger.error(f"Error in cleanup_old_news endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to cleanup old news", "message": str(e)},
        )


@app.post("/api/audio/netspeech")
async def audio_netspeech(request: Request):
    """Forward audio file to NetSpeech API for quality analysis"""
    try:
        # Get the uploaded file from form data
        form = await request.form()
        file = form.get("file")

        if not file:
            return JSONResponse(status_code=400, content={"error": "No file provided"})

        # Read file content
        file_content = await file.read()

        # Forward to NetSpeech API
        NETSPEECH_API_URL = "http://115.79.192.192:19977/get_netspeech"

        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {
                "file": (file.filename, file_content, file.content_type or "audio/wav")
            }
            headers = {"accept": "application/json", "api-key": TTS_API_KEY}

            response = await client.post(
                NETSPEECH_API_URL, files=files, headers=headers
            )

            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": "NetSpeech API error", "details": response.text},
                )

            return JSONResponse(content=response.json())

    except Exception as e:
        logger.error(f"NetSpeech proxy error: {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Proxy error", "message": str(e)}
        )


@app.post("/api/audio/snr")
async def audio_snr(request: Request):
    """Forward audio file to SNR API for signal-to-noise ratio analysis"""
    try:
        # Get the uploaded file from form data
        form = await request.form()
        file = form.get("file")

        if not file:
            return JSONResponse(status_code=400, content={"error": "No file provided"})

        # Read file content
        file_content = await file.read()

        # Forward to SNR API
        SNR_API_URL = "http://115.79.192.192:19977/get_snr"

        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {
                "file": (file.filename, file_content, file.content_type or "audio/wav")
            }
            headers = {"accept": "application/json", "api-key": TTS_API_KEY}

            response = await client.post(SNR_API_URL, files=files, headers=headers)

            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": "SNR API error", "details": response.text},
                )

            return JSONResponse(content=response.json())

    except Exception as e:
        logger.error(f"SNR proxy error: {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Proxy error", "message": str(e)}
        )


@app.post("/api/audio/converter")
async def audio_converter(request: Request):
    """Forward audio file to Audio Converter API with conversion parameters"""
    try:
        # Get the uploaded file and query parameters from form data
        form = await request.form()
        file = form.get("file")

        if not file:
            return JSONResponse(status_code=400, content={"error": "No file provided"})

        # Read file content
        file_content = await file.read()

        # Get query parameters from URL
        sample_rate = request.query_params.get("sample_rate", "22050")
        rate = request.query_params.get("rate", "1.0")
        return_type = request.query_params.get("return_type", "url")
        audio_format = request.query_params.get("audio_format", "wav")

        # Forward to Audio Converter API
        AUDIO_CONVERTER_API_URL = "http://115.79.192.192:19977/audio_converter"

        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {
                "file": (file.filename, file_content, file.content_type or "audio/wav")
            }
            headers = {"accept": "application/json", "api-key": TTS_API_KEY}
            params = {
                "sample_rate": sample_rate,
                "rate": rate,
                "return_type": return_type,
                "audio_format": audio_format,
            }

            response = await client.post(
                AUDIO_CONVERTER_API_URL, files=files, headers=headers, params=params
            )

            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={
                        "error": "Audio Converter API error",
                        "details": response.text,
                    },
                )

            return JSONResponse(content=response.json())

    except Exception as e:
        logger.error(f"Audio Converter proxy error: {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Proxy error", "message": str(e)}
        )


@app.post("/api/audio/generate")
async def audio_generate(
    file: UploadFile = File(...),
    gen_text: str = Form(...),
    ref_lang: str = Form("vi"),
    gen_lang: str = Form("vi"),
    ref_text: Optional[str] = Form(None),
    is_upload: bool = Form(True),
    is_translation: bool = Form(False),
):
    """
    Proxy to external voice cloning API
    Generate audio with cloned voice from reference audio
    """
    try:
        logger.info(f"Voice clone request - gen_text: {gen_text[:50]}...")
        logger.info(f"Languages: ref_lang={ref_lang}, gen_lang={gen_lang}")

        # Read file content
        file_content = await file.read()
        logger.info(f"File uploaded: {file.filename}, size: {len(file_content)} bytes")

        # External voice cloning API URL
        VOICE_CLONE_API_URL = "https://voiceclone-be.namitech.ai/audio/generate/"

        # Get JWT token from external service
        JWT_URL = "https://voiceclone-be.namitech.ai/token"
        token_form_data = {"username": "demo", "password": "Namitech@2025"}

        async with httpx.AsyncClient(timeout=300.0) as client:
            # Get JWT token
            token_response = await client.post(JWT_URL, data=token_form_data)
            if token_response.status_code != 200:
                logger.error(f"Failed to get JWT token: {token_response.status_code}")
                return JSONResponse(
                    status_code=500, content={"error": "Authentication failed"}
                )

            jwt_token = token_response.json()["access_token"]
            logger.info("JWT token obtained successfully")

            # Prepare form data for voice cloning
            form_data = {
                "gen_text": gen_text,
                "ref_lang": ref_lang,
                "gen_lang": gen_lang,
                "is_upload": str(is_upload).lower(),
                "is_translation": str(is_translation).lower(),
            }

            # Add optional ref_text if provided
            if ref_text:
                form_data["ref_text"] = ref_text
                logger.info("Reference text provided")

            # Prepare file for upload
            files = {
                "file": (
                    file.filename,
                    file_content,
                    file.content_type or "audio/wav",
                )
            }

            # Set authorization header
            headers = {"Authorization": f"Bearer {jwt_token}"}

            logger.info(f"Sending request to voice clone API: {VOICE_CLONE_API_URL}")

            # Make request to voice cloning API
            response = await client.post(
                VOICE_CLONE_API_URL, data=form_data, files=files, headers=headers
            )

            logger.info(f"Voice clone API response status: {response.status_code}")

            if response.status_code == 200:
                # Return audio content directly
                return Response(
                    content=response.content,
                    media_type="audio/wav",
                    headers={
                        "Content-Disposition": f'attachment; filename="voice_clone_{file.filename}"'
                    },
                )
            else:
                logger.error(f"Voice clone API error: {response.text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content={
                        "error": "Voice clone generation failed",
                        "details": response.text,
                    },
                )

    except Exception as e:
        logger.error(f"Voice clone proxy error: {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Proxy error", "message": str(e)}
        )


# Vercel serverless handler - Use ASGI interface directly
app_handler = app
