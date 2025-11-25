# Backend Authentication Server

FastAPI-based authentication server for the TTS demo application with JWT token authentication.

## Features

- Dual authentication: Username/password OR email/password
- Email domain restriction (@namisense.ai only)
- JWT token-based authentication (stateless)
- Login/Logout/Verify endpoints
- Automatic API documentation (Swagger UI)
- CORS enabled for local development
- Type-safe with Pydantic models
- Demo user accounts

## Installation

1. Create a virtual environment (if not already created):
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

## Running the Server

```bash
python server.py
```

The server will start on `http://localhost:5000`

**API Documentation:**
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## Demo Credentials

The following demo accounts are available:

**Username/Password:**
- **Username:** admin | **Password:** admin123
- **Username:** demo  | **Password:** demo123
- **Username:** user  | **Password:** password

**Email/Password (@namisense.ai only):**
- **Email:** admin@namisense.ai | **Password:** admin123
- **Email:** user@namisense.ai  | **Password:** password123
- **Email:** demo@namisense.ai  | **Password:** demo123

## API Endpoints

### POST /api/login
Authenticate user and return JWT token (supports both username and email)

**Request:**
```json
{
  "identifier": "admin",
  "password": "admin123"
}
```

Or with email:
```json
{
  "identifier": "admin@namisense.ai",
  "password": "admin123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "email": "admin@namisense.ai"
  }
}
```

**Response (Invalid Email Domain):**
```json
{
  "detail": "Only namisense.ai email addresses are allowed"
}
```
**Status:** 403 Forbidden

**Response (Invalid Credentials):**
```json
{
  "detail": "Invalid credentials"
}
```
**Status:** 401 Unauthorized

### POST /api/logout
Logout endpoint (client handles token removal)

**Request Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "success": true
}
```

### GET /api/session
### GET /api/verify
Verify JWT token and return authentication status

**Request Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response (Authenticated):**
```json
{
  "authenticated": true,
  "user": {
    "username": "admin",
    "email": "admin@namisense.ai"
  }
}
```

**Response (Not Authenticated):**
```json
{
  "authenticated": false,
  "user": null
}
```

### GET /api/health
Health check endpoint

**Response:**
```json
{
  "status": "ok"
}
```

## Notes

- Built with FastAPI (modern async Python framework)
- Uses JWT (JSON Web Tokens) for stateless authentication
- Tokens expire after 24 hours
- Tokens stored in sessionStorage (cleared on browser close)
- Supports both username/password and email/password authentication
- Email addresses must be from @namisense.ai domain
- CORS configured for `http://localhost:5173` (Vite) and `http://localhost:3000`
- Interactive API docs available at `/docs` and `/redoc`
- In production: Use HTTPS, rotate JWT secrets, use environment variables


