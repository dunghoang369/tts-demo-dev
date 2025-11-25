from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
import re
import httpx
import firebase_admin
from firebase_admin import credentials, firestore
import logging

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

# CORS configuration - allow all origins for flexible deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
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
        return None


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
        async with httpx.AsyncClient(timeout=300.0) as client:
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
    1. Fetch news from API
    2. Summarize each article
    3. Upload to Firestore
    Returns: dict with processing statistics
    """
    try:
        # Get category mapping
        news_category = await get_news_category()
        category = news_category.get(news_type, {}).get("category", news_type)

        # Fetch news
        news = await get_news(news_type, limit)
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

        news_items = []
        fetch_date = datetime.now().isoformat()
        failed_count = 0

        for article in articles:
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
                            f"{publish_date} {publish_time_str}", "%d/%m/%Y %H:%M"
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

        return {
            "category": category,
            "articles": len(articles),
            "uploaded": uploaded_count,
            "failed": failed_count,
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

        # Forward to external TTS API
        API_URL = "http://115.79.192.192:19977/invocations"
        API_KEY = "zNBVyiatKn5eTvC2CEvDg1msgOCHrTZ55zZ0qfsu"

        async with httpx.AsyncClient(timeout=30.0) as client:
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

            # Return the JSON response from TTS API
            return JSONResponse(content=response.json())

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": "Proxy error", "message": str(e)}
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
            date_obj = datetime.fromtimestamp(most_recent_timestamp)
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

            if not category or not publish_time:
                continue

            # Filter: only include articles from last 7 days
            if publish_time < seven_days_timestamp:
                continue

            # Format date
            date_obj = datetime.fromtimestamp(publish_time)
            formatted_date = date_obj.strftime("%d/%m/%Y")

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
                            merged_content += f"- {title}: {summary}\n\n"

                    # Create entry for this date
                    date_entry = {
                        "date": date_str,
                        "title": f"Tin tức {category_name} - {date_str}",
                        "content": merged_content.strip(),
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
                    # Convert to ISO format string
                    result["last_updated"] = last_crawl
                else:
                    result["last_updated"] = datetime.now().isoformat()
            else:
                result["last_updated"] = datetime.now().isoformat()
        except Exception as e:
            logger.error(f"Error fetching metadata: {e}")
            result["last_updated"] = datetime.now().isoformat()

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


# Vercel serverless handler - Use ASGI interface directly
app_handler = app
