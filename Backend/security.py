import os
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer

# Load the secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in .env file")

# Setup for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setup for token generation
serializer = URLSafeTimedSerializer(SECRET_KEY)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def generate_reset_token(email: str) -> str:
    """Generates a secure, timed token for password reset."""
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token: str, max_age_seconds: int = 3600) -> str | None:
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