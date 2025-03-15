import os
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import business_cards
from app.config import API_V1_PREFIX, UPLOAD_DIR
from app.db.session import Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Handle Google Cloud credentials
try:
    # If GOOGLE_CREDENTIALS_JSON env var exists (Render deployment)
    if os.environ.get("GOOGLE_CREDENTIALS_JSON"):
        logger.info("Found credentials in GOOGLE_CREDENTIALS_JSON environment variable")

        # Use /tmp for Render deployment, but fall back to local path if needed
        is_render = not os.environ.get("DEBUG", "").lower() == "true"
        credentials_path = "/tmp/google-credentials.json" if is_render else "./google-credentials.json"

        try:
            # Parse and re-serialize to ensure valid JSON
            credentials_json = json.loads(os.environ.get("GOOGLE_CREDENTIALS_JSON"))

            with open(credentials_path, "w") as f:
                json.dump(credentials_json, f)

            # Set environment variable to point to file
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            logger.info(f"Credentials written to {credentials_path}")

            # Verify file was created and has content
            if os.path.exists(credentials_path):
                file_size = os.path.getsize(credentials_path)
                logger.info(f"Confirmed file exists with size: {file_size} bytes")
            else:
                logger.error(f"File was not created at {credentials_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in environment variable: {str(e)}")
        except Exception as e:
            logger.error(f"Error writing credentials file: {str(e)}")

    # Check if credentials file exists at the path in GOOGLE_APPLICATION_CREDENTIALS
    elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if os.path.exists(creds_path):
            logger.info(f"Using credentials from {creds_path}")
        else:
            logger.error(f"Credentials file not found at {creds_path}")
            raise FileNotFoundError(f"Credentials file not found at {creds_path}")

    # Check for credentials file in current directory (local development)
    elif os.path.exists("./google-credentials.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-credentials.json"
        logger.info("Using credentials from ./google-credentials.json")

    # No credentials found
    else:
        logger.error("No Google Cloud credentials found")
        raise FileNotFoundError("No Google Cloud credentials found")
except Exception as e:
    logger.error(f"Error setting up Google Cloud credentials: {str(e)}")
    # Continue execution to allow the app to start and show proper error messages

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Business Card OCR API",
    description="API for processing business cards using OCR",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(
    business_cards.router,
    prefix=f"{API_V1_PREFIX}/business-cards",
    tags=["business-cards"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the Business Card OCR API"}

@app.get("/health")
def health_check():
    # Check if Google credentials are working
    creds_status = "available" if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") else "missing"
    if creds_status == "available":
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if os.path.exists(creds_path):
            creds_status = "valid"
        else:
            creds_status = f"file not found at {creds_path}"

    # Get Google credentials environment info
    google_creds_env = "set" if os.environ.get("GOOGLE_CREDENTIALS_JSON") else "missing"
    google_app_creds_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "missing")

    # Check temp file and local file
    tmp_file_exists = os.path.exists("/tmp/google-credentials.json")
    local_file_exists = os.path.exists("./google-credentials.json")

    return {
        "status": "healthy",
        "google_credentials": creds_status,
        "google_creds_env": google_creds_env,
        "google_app_creds_env": google_app_creds_env,
        "tmp_file_exists": tmp_file_exists,
        "local_file_exists": local_file_exists,
        "environment": "production" if not os.environ.get("DEBUG") else "development"
    }

@app.get("/check-credentials")
def check_credentials():
    """Detailed check of Google credential status"""
    results = {
        "env_vars": {
            "GOOGLE_CREDENTIALS_JSON": bool(os.environ.get("GOOGLE_CREDENTIALS_JSON")),
            "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "not set"),
            "DEBUG": os.environ.get("DEBUG", "not set")
        },
        "files": {}
    }

    # Check temp file
    tmp_path = "/tmp/google-credentials.json"
    if os.path.exists(tmp_path):
        results["files"][tmp_path] = {
            "exists": True,
            "size": os.path.getsize(tmp_path),
            "readable": os.access(tmp_path, os.R_OK)
        }
    else:
        results["files"][tmp_path] = {"exists": False}

    # Check local file
    local_path = "./google-credentials.json"
    if os.path.exists(local_path):
        results["files"][local_path] = {
            "exists": True,
            "size": os.path.getsize(local_path),
            "readable": os.access(local_path, os.R_OK)
        }
    else:
        results["files"][local_path] = {"exists": False}

    return results
