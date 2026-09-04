import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend root if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "RecoverX - AI Revenue Recovery Agent"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Environment & Database
    ENV: str = os.getenv("ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/recoverx.db")
    
    # Authentication & Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "recoverx-super-secret-jwt-key-2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Razorpay Test Mode Credentials
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_recoverxDemoKey123")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "recoverxSecretKeyDemoTestMode999")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "webhook_secret_demo_987654321")
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Default Policy Rules (per Track 03 requirements)
    DEFAULT_MAX_AUTONOMOUS_AMOUNT: float = 50000.0  # ₹50,000 ceiling
    DEFAULT_RECOVERY_WINDOW_HOURS: int = 72         # 72 hours window
    DEFAULT_MAX_RECOVERY_ATTEMPTS: int = 2          # 2 contact attempts
    DEFAULT_MAX_VOICE_ATTEMPTS: int = 1             # 1 voice attempt
    DEFAULT_OPT_OUT_BEHAVIOR: str = "DO_NOT_CONTACT"
    DEFAULT_VOICE_ENABLED: bool = True
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:3000",
        "http://localhost:4000",
    ]

settings = Settings()
