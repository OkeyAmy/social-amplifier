# Social Amplifier Backend

Python-based REST API for the Social Amplifier platform with LinkedIn and X (Twitter) integration.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Required Credentials:**

- **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **LinkedIn OAuth**:
  1. Create app at [LinkedIn Developers](https://www.linkedin.com/developers/apps)
  2. Add redirect URI: `http://localhost:8000/api/v1/auth/linkedin/callback`
  3. Request permissions: `r_liteprofile`, `r_emailaddress`, `w_member_social`
- **X (Twitter) OAuth 2.0**:
  1. Create app at [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
  2. Enable OAuth 2.0 with PKCE
  3. Add redirect URI: `http://localhost:8000/api/v1/auth/twitter/callback`
  4. Request scopes: `tweet.read`, `tweet.write`, `users.read`, `offline.access`

### 3. Initialize Database

```bash
python -m app.database.init_db
```

### 4. Run the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   └── dependencies.py  # Dependency injection
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── security.py      # Authentication & encryption
│   │   └── exceptions.py    # Custom exceptions
│   ├── database/
│   │   ├── models.py        # SQLAlchemy models
│   │   └── init_db.py       # Database initialization
│   ├── services/
│   │   ├── gemini.py        # AI content generation
│   │   ├── linkedin.py      # LinkedIn API integration
│   │   ├── twitter.py       # X (Twitter) API integration
│   │   └── content.py       # Content processing logic
│   └── schemas/             # Pydantic schemas
├── main.py                  # Application entry point
├── requirements.txt
└── .env
```

## Testing the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Generate LinkedIn Content
```bash
curl -X POST http://localhost:8000/api/v1/generate/linkedin \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "I am feeling peackish today",
    "emoji": "🍑",
    "mode": "standard"
  }'
```

### 3. Generate Twitter Content
```bash
curl -X POST http://localhost:8000/api/v1/generate/twitter \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "I am feeling peackish today",
    "emoji": "🍑",
    "mode": "single"
  }'
```

## OAuth Flow

### LinkedIn
1. Frontend redirects to: `GET /api/v1/auth/linkedin/connect`
2. User authorizes on LinkedIn
3. LinkedIn redirects to callback with code
4. Backend exchanges code for tokens
5. Returns session token to frontend

### X (Twitter)
1. Frontend redirects to: `GET /api/v1/auth/twitter/connect`
2. User authorizes on X
3. X redirects to callback with code
4. Backend exchanges code for tokens (using PKCE)
5. Returns session token to frontend

## Security Notes

- All OAuth tokens are encrypted using AES-256
- Session tokens expire after 30 minutes of inactivity
- Rate limiting is applied to all endpoints
- CORS is configured for allowed origins only
- Passwords are never stored (OAuth only)

## Deployment

For production deployment:
1. Use a proper PostgreSQL database instead of SQLite
2. Set strong SECRET_KEY and ENCRYPTION_KEY
3. Configure proper CORS origins
4. Use HTTPS for all OAuth callbacks
5. Set up proper logging and monitoring
6. Consider using Redis for session storage
