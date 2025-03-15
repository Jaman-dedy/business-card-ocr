# 🪪 Business Card OCR API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

A robust API for extracting information from business cards using OCR (Optical Character Recognition) powered by Google Cloud Vision API.

## ✨ Features

- 📷 Upload business card images
- 🔍 Extract text using Google Cloud Vision OCR
- 🧠 AI-powered information extraction
- 💾 Store extracted data in PostgreSQL database
- 📊 Retrieve and manage business card information
- 🐳 Containerized with Docker
- 📚 Comprehensive API documentation with Swagger UI

## 🛠️ Technology Stack

- **Backend**: FastAPI
- **OCR Engine**: Google Cloud Vision API
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Container**: Docker
- **Deployment**: Render

## 📋 Prerequisites

- Docker and Docker Compose
- Google Cloud account with Vision API enabled
- Google Cloud service account with credentials

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Jaman-dedy/business-card-ocr.git
cd business-card-ocr
```

### 2. Set up Google Cloud Vision API

1. Create a project in Google Cloud Console
2. Enable the Cloud Vision API
3. Create a service account with the "Basic > Editor" role
4. Download the service account JSON key
5. Rename the key to `google-credentials.json` and place it in the project root

### 3. Configure environment variables

Create a `.env` file in the project root:

```
# Database configuration
DATABASE_URL=postgresql://postgres:password@db:5432/business_cards

# Google Cloud Vision API
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json

# API settings
API_PREFIX=/api/v1
DEBUG=True
```

### 4. Start the services

```bash
make build  # Build the Docker containers
make up     # Start the services
```

The API will be available at http://localhost:8000

## 📚 API Documentation

Interactive API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📋 Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| POST | `/api/v1/business-cards/` | Upload and process a business card |
| GET | `/api/v1/business-cards/{id}` | Get a specific business card |
| GET | `/api/v1/business-cards/` | List all business cards |
| DELETE | `/api/v1/business-cards/{id}` | Delete a business card |

## 🧰 Development

### Common Commands

```bash
# Start services
make up

# View logs
make logs

# Access the database
make db-shell

# Run migrations
make migrate

# Stop services
make down

# Clean up
make clean
```

For a full list of commands, run `make help`.

## 📦 Project Structure

```
business-card-ocr/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI entry point
│   ├── config.py           # Configuration settings
│   ├── api/                # API endpoints
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── business_cards.py
│   ├── core/               # Core business logic
│   │   ├── __init__.py
│   │   └── ocr.py          # Google Vision integration
│   ├── db/                 # Database models and connection
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── models.py
│   └── schemas/            # Pydantic models
│       ├── __init__.py
│       └── business_card.py
├── migrations/             # Alembic migrations
├── uploads/                # Uploaded business card images
├── .env                    # Environment variables
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## 🚀 Deployment

### Deploying to Render

1. Push your code to GitHub
2. Create a PostgreSQL database in Render
3. Create a Web Service in Render connected to your GitHub repository
4. Add the following environment variables:
   - `DATABASE_URL`: Your Render PostgreSQL connection string
   - `GOOGLE_APPLICATION_CREDENTIALS`: Upload your credentials as an environment secret
   - `API_PREFIX`: `/api/v1`
   - `DEBUG`: `false`

## 📝 License

MIT

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ✨ Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Cloud Vision API](https://cloud.google.com/vision)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Docker](https://www.docker.com/)
- [Render](https://render.com/)
