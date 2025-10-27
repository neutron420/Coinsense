"""
FastAPI main application for Crypto AI Chatbot
"""
from fastapi import FastAPI
from dotenv import load_dotenv 
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
from contextlib import asynccontextmanager

from config import settings
from database import engine, Base
from .routes import chat, predict, sentiment, auth
from auth import get_current_user
from models import User

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Crypto AI Chatbot...")
    print(f"📊 Database: {settings.database_url}")
    print(f"🔑 JWT Secret: {'*' * len(settings.secret_key)}")
    yield
    # Shutdown
    print("👋 Shutting down Crypto AI Chatbot...")

# Initialize FastAPI app
app = FastAPI(
    title="Crypto AI Chatbot API",
    description="AI-powered cryptocurrency analysis and assistance",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(predict.router, prefix="/api/predict", tags=["Prediction"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["Sentiment"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": " Crypto AI Chatbot API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "auth": "/api/auth",
            "chat": "/api/chat",
            "predict": "/api/predict",
            "sentiment": "/api/sentiment",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "models": "loaded"
    }

@app.get("/api/user/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
