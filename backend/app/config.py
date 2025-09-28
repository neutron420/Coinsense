"""
Configuration settings for the Crypto AI Chatbot
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    database_url: str = "postgresql://username:password@localhost:5432/coinsense_db"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "coinsense_db"
    db_user: str = "username"
    db_password: str = "password"
    
    # JWT Configuration
    secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Keys
    coingecko_api_key: str = "your-coingecko-api-key"
    news_api_key: str = "your-newsapi-key"
    coinmarketcap_api_key: str = "your-coinmarketcap-api-key"
    huggingface_api_key: str = "your-huggingface-api-key"
    
    # Model Configuration
    lstm_model_path: str = "./models/lstm_model.pth"
    rag_model_path: str = "./models/rag_model"
    sentiment_model_path: str = "./models/sentiment_model"
    
    # Data Paths
    crypto_dataset_path: str = "./datasets/crypto_datasets/Cryptocurrency_Dataset_2023.csv"
    coins_data_path: str = "./datasets/coins_datasets/"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # ML Model Settings
    lstm_sequence_length: int = 60
    lstm_hidden_size: int = 50
    lstm_num_layers: int = 2
    lstm_dropout: float = 0.2
    
    # RAG Settings
    rag_model_name: str = "all-MiniLM-L6-v2"
    rag_top_k: int = 5
    rag_confidence_threshold: float = 0.5
    
    # Sentiment Analysis Settings
    sentiment_model_name: str = "ProsusAI/finbert"
    sentiment_max_length: int = 512
    sentiment_batch_size: int = 16
    
    # News API Settings
    news_max_articles: int = 10
    news_language: str = "en"
    news_sort_by: str = "publishedAt"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # Security
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    
    # Cache Settings
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 1000
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".csv", ".json", ".txt"]
    
    # Model Training
    training_epochs: int = 100
    training_batch_size: int = 32
    training_learning_rate: float = 0.001
    training_validation_split: float = 0.2
    
    # Prediction Settings
    max_prediction_days: int = 7
    prediction_confidence_threshold: float = 0.6
    
    # Sentiment Analysis
    sentiment_confidence_threshold: float = 0.7
    sentiment_positive_threshold: float = 0.6
    sentiment_negative_threshold: float = -0.6
    
    @validator('allowed_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('database_url', pre=True)
    def build_database_url(cls, v, values):
        # If DATABASE_URL is explicitly set and not the default, use it
        if v and v != "postgresql://username:password@localhost:5432/coinsense_db":
            return v
        
        # If using SQLite, return the SQLite URL
        if v and v.startswith("sqlite://"):
            return v
        
        # Build PostgreSQL URL from individual components (fallback)
        host = values.get('db_host', 'localhost')
        port = values.get('db_port', 5432)
        name = values.get('db_name', 'coinsense_db')
        user = values.get('db_user', 'username')
        password = values.get('db_password', 'password')
        
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Validate settings
def validate_settings():
    """Validate application settings"""
    errors = []
    
    # Check required API keys
    if settings.coingecko_api_key == "your-coingecko-api-key":
        errors.append("COINGECKO_API_KEY not set")
    
    if settings.news_api_key == "your-newsapi-key":
        errors.append("NEWS_API_KEY not set")
    
    # Check secret key
    if settings.secret_key == "your-super-secret-jwt-key-change-this-in-production":
        errors.append("SECRET_KEY not changed from default")
    
    # Check database URL
    if "username:password" in settings.database_url:
        errors.append("Database credentials not configured")
    
    if errors:
        print("⚠️  Configuration Warnings:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease update your .env file with proper values.")
    
    return len(errors) == 0

# Validate on import
if __name__ == "__main__":
    validate_settings()
else:
    validate_settings()
