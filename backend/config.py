import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY", "")
    
    # BioBERT Model
    BIOBERT_MODEL = "dmis-lab/biobert-v1.1"
    
    # Database
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME = "physio_chatbot"
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Data Paths
    ASSESSMENTS_PATH = "data/assessments"
    EXERCISES_PATH = "data/exercises"
    
    # Weaviate Schema
    WEAVIATE_CLASS_NAME = "PhysioKnowledge"