import os
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# API settings
API_V1_PREFIX = os.getenv("API_PREFIX", "/api/v1")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL")

# Google Cloud Vision API credential handling
# Check for JSON credentials in environment variable first (for Render)
if os.environ.get("GOOGLE_CREDENTIALS_JSON"):
    logger.info("Config: Found Google credentials in environment variable")
    credentials_path = "/tmp/google-credentials.json"
    GOOGLE_APPLICATION_CREDENTIALS = credentials_path
# Then check for path in environment variable
elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    logger.info(f"Config: Using Google credentials path from environment: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
# Finally check for local file (development)
elif os.path.exists("./google-credentials.json"):
    logger.info("Config: Using local Google credentials file")
    GOOGLE_APPLICATION_CREDENTIALS = "./google-credentials.json"
else:
    logger.warning("Config: No Google credentials found")
    GOOGLE_APPLICATION_CREDENTIALS = None

# Log credential path for debugging
logger.info(f"Config: GOOGLE_APPLICATION_CREDENTIALS set to: {GOOGLE_APPLICATION_CREDENTIALS}")

# Upload settings
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
