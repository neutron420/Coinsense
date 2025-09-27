"""
SQLAlchemy models for the Crypto AI Chatbot
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")

class ChatHistory(Base):
    """Chat history model to store user conversations"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), index=True, nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    message_type = Column(String(50), default="general")  # general, prediction, sentiment
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_history")

class Prediction(Base):
    """Model to store price predictions"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cryptocurrency = Column(String(20), nullable=False)  # BTC, ETH, etc.
    current_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    actual_price = Column(Float, nullable=True)  # For future validation
    accuracy = Column(Float, nullable=True)  # Calculated accuracy
    
    # Relationships
    user = relationship("User", back_populates="predictions")

class SentimentAnalysis(Base):
    """Model to store sentiment analysis results"""
    __tablename__ = "sentiment_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    news_source = Column(String(100), nullable=False)
    sentiment_score = Column(Float, nullable=False)  # -1 to 1
    sentiment_label = Column(String(20), nullable=False)  # positive, negative, neutral
    confidence = Column(Float, nullable=False)
    news_text = Column(Text, nullable=True)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")

class CryptoData(Base):
    """Model to store cryptocurrency data cache"""
    __tablename__ = "crypto_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    current_price = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    price_change_24h = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

class ModelMetrics(Base):
    """Model to store ML model performance metrics"""
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(50), nullable=False)  # lstm, rag, sentiment
    model_version = Column(String(20), nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    mse = Column(Float, nullable=True)  # For regression models
    mae = Column(Float, nullable=True)  # For regression models
    created_at = Column(DateTime(timezone=True), server_default=func.now())
