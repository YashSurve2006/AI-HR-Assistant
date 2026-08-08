"""Application configuration."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Flask
DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
PORT = int(os.environ.get("FLASK_PORT", 5000))

# Paths
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATABASE_PATH = os.path.join(BASE_DIR, "hr_assistant.db")

# CORS
CORS_ORIGINS = [
    "http://127.0.0.1:8080", "http://localhost:8080",
    "http://127.0.0.1:5500", "http://localhost:5500",
    "http://127.0.0.1:5000", "http://localhost:5000",
    # Allow file:// protocol (origin is 'null') for direct HTML file opening
    "null",
]
