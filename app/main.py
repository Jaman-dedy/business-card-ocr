import os
import json
import logging
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import business_cards
from app.config import API_V1_PREFIX, UPLOAD_DIR
from app.db.session import Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug information - will appear in logs
logger.info(f"Current working directory: {os.getcwd()}")
try:
    logger.info(f"Files in current directory: {', '.join(os.listdir('.'))}")
    logger.info(f"Files in /tmp directory: {', '.join(os.listdir('/tmp'))}")
except Exception as e:
    logger.error(f"Error listing directory contents: {str(e)}")

# Handle Google Cloud credentials
try:
    # Always use /tmp for Render deployment
    credentials_path = "/tmp/google-credentials.json"

    # If GOOGLE_CREDENTIALS_JSON env var exists
    if os.environ.get("GOOGLE_CREDENTIALS_JSON"):
        logger.info("Found credentials in GOOGLE_CREDENTIALS_JSON environment variable")

        try:
            # Parse and re-serialize to ensure valid JSON
            credentials_json = json.loads(os.environ.get("GOOGLE_CREDENTIALS_JSON"))

            # Write to /tmp directory which should be writable in all environments
            with open(credentials_path, "w") as f:
                json.dump(credentials_json, f)

            # Make sure file permissions are correct
            os.chmod(credentials_path, 0o600)

            # Set environment variable to point to file
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            logger.info(f"Credentials written to {credentials_path}")

            # Verify file was created and has content
            if os.path.exists(credentials_path):
                file_size = os.path.getsize(credentials_path)
                logger.info(f"Confirmed credentials file exists with size: {file_size} bytes")
            else:
                logger.error(f"Credentials file was not created at {credentials_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in environment variable: {str(e)}")
        except Exception as e:
            logger.error(f"Error writing credentials file: {str(e)}")

    # Check if credentials file exists at the path in GOOGLE_APPLICATION_CREDENTIALS
    elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        logger.info(f"Using credentials path from GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")

        if os.path.exists(creds_path):
            logger.info(f"Confirmed credentials file exists at {creds_path}")
        else:
            logger.error(f"Credentials file not found at {creds_path}")

            # Try finding credentials in standard locations as fallback
            potential_paths = [
                "./google-credentials.json",
                "/app/google-credentials.json",
                "/tmp/google-credentials.json"
            ]

            for path in potential_paths:
                if os.path.exists(path):
                    logger.info(f"Found credentials file at {path}")
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
                    break
            else:
                raise FileNotFoundError(f"Credentials file not found at {creds_path} or any standard locations")

    # Check for credentials file in current directory (local development)
    elif os.path.exists("./google-credentials.json"):
        local_creds_path = "./google-credentials.json"
        logger.info(f"Found local credentials at {local_creds_path}")

        # Copy to /tmp for consistency across environments
        try:
            with open(local_creds_path, 'r') as src_file:
                with open(credentials_path, 'w') as dest_file:
                    dest_file.write(src_file.read())
            os.chmod(credentials_path, 0o600)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            logger.info(f"Copied local credentials to {credentials_path}")
        except Exception as e:
            logger.error(f"Error copying credentials: {str(e)}")
            # Fall back to using local path
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_creds_path
            logger.info(f"Using local credentials from {local_creds_path}")

    # No credentials found
    else:
        logger.error("No Google Cloud credentials found in any location")
        raise FileNotFoundError("No Google Cloud credentials found")

except Exception as e:
    logger.error(f"Error setting up Google Cloud credentials: {str(e)}")
    # Continue execution to allow the app to start and show proper error messages

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")

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
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    logger.info(f"Ensured upload directory exists at {UPLOAD_DIR}")
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
except Exception as e:
    logger.error(f"Error mounting uploads directory: {str(e)}")

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
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "not set")

    creds_status = {
        "path": creds_path,
        "exists": os.path.exists(creds_path) if creds_path != "not set" else False,
        "is_file": os.path.isfile(creds_path) if creds_path != "not set" else False,
        "size": os.path.getsize(creds_path) if creds_path != "not set" and os.path.exists(creds_path) else 0,
        "readable": os.access(creds_path, os.R_OK) if creds_path != "not set" and os.path.exists(creds_path) else False
    }

    # Check all potential credential locations
    credential_files = {
        "/tmp/google-credentials.json": os.path.exists("/tmp/google-credentials.json"),
        "./google-credentials.json": os.path.exists("./google-credentials.json"),
        "/app/google-credentials.json": os.path.exists("/app/google-credentials.json")
    }

    return {
        "status": "healthy",
        "environment": "production" if not os.environ.get("DEBUG") else "development",
        "working_directory": os.getcwd(),
        "google_credentials_status": creds_status,
        "potential_credential_files": credential_files,
        "env_vars": {
            "GOOGLE_CREDENTIALS_JSON": bool(os.environ.get("GOOGLE_CREDENTIALS_JSON")),
            "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "not set"),
        }
    }

@app.get("/debug")
def debug_info():
    """Detailed system information for debugging"""
    try:
        return {
            "system": {
                "current_dir": os.getcwd(),
                "files_in_current_dir": os.listdir('.'),
                "files_in_tmp": os.listdir('/tmp'),
            },
            "environment_variables": {
                key: value for key, value in os.environ.items()
                if not key.startswith("GOOGLE") and not "KEY" in key.upper() and not "SECRET" in key.upper()
            },
            "credential_paths": {
                "tmp_path": {
                    "exists": os.path.exists("/tmp/google-credentials.json"),
                    "size": os.path.getsize("/tmp/google-credentials.json") if os.path.exists("/tmp/google-credentials.json") else 0,
                    "permissions": oct(os.stat("/tmp/google-credentials.json").st_mode)[-3:] if os.path.exists("/tmp/google-credentials.json") else "N/A"
                },
                "local_path": {
                    "exists": os.path.exists("./google-credentials.json"),
                    "size": os.path.getsize("./google-credentials.json") if os.path.exists("./google-credentials.json") else 0,
                    "permissions": oct(os.stat("./google-credentials.json").st_mode)[-3:] if os.path.exists("./google-credentials.json") else "N/A"
                },
                "app_path": {
                    "exists": os.path.exists("/app/google-credentials.json"),
                    "size": os.path.getsize("/app/google-credentials.json") if os.path.exists("/app/google-credentials.json") else 0,
                    "permissions": oct(os.stat("/app/google-credentials.json").st_mode)[-3:] if os.path.exists("/app/google-credentials.json") else "N/A"
                }
            },
            "python_info": {
                "version": sys.version,
                "path": sys.path
            }
        }
    except Exception as e:
        return {"error": str(e)}
