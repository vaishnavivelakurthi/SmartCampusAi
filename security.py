import re
import bcrypt
from email_validator import validate_email as val_email, EmailNotValidError

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a password against its bcrypt hash."""
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Validates email format using the email-validator library."""
    try:
        val_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False

def validate_phone(phone: str) -> bool:
    """Validates phone numbers using a standard regex pattern."""
    # Matches international format: +1234567890 or local formats with spaces, hyphens, and parenthesis
    pattern = r'^\+?[0-9\s\-()]{7,18}$'
    return bool(re.match(pattern, phone.strip()))

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Ensures password meets standard security criteria (min 6 characters)."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""
