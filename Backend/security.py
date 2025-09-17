import os
import time
import re
from typing import Optional, Dict
import os
import redis
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
import jwt

# Load the secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Defer hard failure to when app starts to ease tooling; still guard usage
    SECRET_KEY = "__MISSING_SECRET_KEY__"

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60  # 1 hour

# Setup for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setup for token generation (for password reset)
serializer = URLSafeTimedSerializer(SECRET_KEY)

# ---------------- Password hashing -----------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# ---------------- Password policy ------------------
PASSWORD_POLICY_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+\-=]{8,64}$")

def validate_password_policy(password: str) -> Optional[str]:
    """Return None if valid, else an error message."""
    if not PASSWORD_POLICY_RE.match(password):
        return (
            "Password must be 8-64 chars, include at least one letter and one digit."
        )
    return None

# ---------------- Reset token (email) ---------------
def generate_reset_token(email: str) -> str:
    """Generates a secure, timed token for password reset."""
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token: str, max_age_seconds: int = 3600) -> Optional[str]:
    """Verifies the reset token and returns the email if valid."""
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=max_age_seconds
        )
        return email
    except Exception:
        return None

# ---------------- JWT access tokens -----------------
def create_access_token(*, user_id: int, username: str, email: str) -> str:
    if SECRET_KEY == "__MISSING_SECRET_KEY__":
        raise RuntimeError("SECRET_KEY is not configured")
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "username": username,
        "email": email,
        "iat": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_access_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:
        return None

# ---------------- Simple in-memory rate limit -------
_RATE_BUCKET: Dict[str, list] = {}
_REDIS_URL = os.getenv("REDIS_URL")
_redis_client = None
if _REDIS_URL:
    try:
        _redis_client = redis.Redis.from_url(_REDIS_URL, decode_responses=True)
        _redis_client.ping()
    except Exception:
        _redis_client = None

def rate_limit_ok(key: str, max_requests: int, window_seconds: int) -> bool:
    """Use Redis token bucket when available; fallback to in-memory."""
    if _redis_client is not None:
        pipeline = _redis_client.pipeline()
        try:
            pipeline.incr(key)
            pipeline.expire(key, window_seconds)
            count, _ = pipeline.execute()
            return int(count) <= max_requests
        except Exception:
            # fall back to memory
            pass
    # In-memory fallback
    now = time.time()
    bucket = _RATE_BUCKET.setdefault(key, [])
    _RATE_BUCKET[key] = [ts for ts in bucket if ts > now - window_seconds]
    if len(_RATE_BUCKET[key]) >= max_requests:
        return False
    _RATE_BUCKET[key].append(now)
    return True