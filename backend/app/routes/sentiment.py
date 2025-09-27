"""
Sentiment analysis routes for the Crypto AI Chatbot
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from database import get_db
from models import User, SentimentAnalysis
from auth import get_current_user
from ml.sentiment_model import get_sentiment_analyzer
from utils import sanitize_input

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models
class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    label: str
    score: float
    confidence: float
    text: str
    analysis_date: str

class MarketSentimentRequest(BaseModel):
    query: str = "cryptocurrency"
    max_articles: int = 10

class MarketSentimentResponse(BaseModel):
    overall_sentiment: str
    confidence: float
    positive_count: int
    negative_count: int
    neutral_count: int
    total_articles: int
    sentiment_score: float
    analysis_date: str
    articles_analyzed: List[dict]

class SentimentHistory(BaseModel):
    id: int
    news_source: str
    sentiment_score: float
    sentiment_label: str
    confidence: float
    analysis_date: str

class ModelInfo(BaseModel):
    model_name: str
    device: str
    max_length: int
    supports_batch: bool
    model_type: str

@router.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(
    sentiment_request: SentimentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze sentiment of a single text"""
    try:
        # Sanitize input
        sanitized_text = sanitize_input(sentiment_request.text)
        if not sanitized_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        # Get sentiment analyzer
        analyzer = get_sentiment_analyzer()
        
        # Analyze sentiment
        result = analyzer.analyze_sentiment(sanitized_text)
        
        # Save to database
        sentiment_record = SentimentAnalysis(
            user_id=current_user.id,
            news_source="user_input",
            sentiment_score=result.score,
            sentiment_label=result.label,
            confidence=result.confidence,
            news_text=sanitized_text
        )
        
        db.add(sentiment_record)
        db.commit()
        db.refresh(sentiment_record)
        
        return SentimentResponse(
            label=result.label,
            score=result.score,
            confidence=result.confidence,
            text=sanitized_text,
            analysis_date=result.timestamp.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentiment analysis failed: {str(e)}"
        )

@router.post("/market-sentiment", response_model=MarketSentimentResponse)
async def get_market_sentiment(
    market_request: MarketSentimentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall market sentiment from news"""
    try:
        # Validate max_articles
        if market_request.max_articles < 1 or market_request.max_articles > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Max articles must be between 1 and 50"
            )
        
        # Get sentiment analyzer
        analyzer = get_sentiment_analyzer()
        
        # Get market sentiment
        sentiment_result = analyzer.get_market_sentiment(
            query=market_request.query,
            max_articles=market_request.max_articles
        )
        
        # Save overall sentiment to database
        sentiment_record = SentimentAnalysis(
            user_id=current_user.id,
            news_source="market_analysis",
            sentiment_score=sentiment_result['sentiment_score'],
            sentiment_label=sentiment_result['overall_sentiment'],
            confidence=sentiment_result['confidence'],
            news_text=f"Market sentiment analysis for query: {market_request.query}"
        )
        
        db.add(sentiment_record)
        db.commit()
        
        return MarketSentimentResponse(
            overall_sentiment=sentiment_result['overall_sentiment'],
            confidence=sentiment_result['confidence'],
            positive_count=sentiment_result['positive_count'],
            negative_count=sentiment_result['negative_count'],
            neutral_count=sentiment_result['neutral_count'],
            total_articles=sentiment_result['total_articles'],
            sentiment_score=sentiment_result['sentiment_score'],
            analysis_date=sentiment_result['analysis_date'],
            articles_analyzed=sentiment_result.get('articles_analyzed', [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market sentiment analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market sentiment analysis failed: {str(e)}"
        )

@router.get("/crypto-sentiment/{crypto_name}")
async def get_crypto_sentiment(
    crypto_name: str,
    max_articles: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sentiment for a specific cryptocurrency"""
    try:
        if max_articles < 1 or max_articles > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Max articles must be between 1 and 50"
            )
        
        # Get sentiment analyzer
        analyzer = get_sentiment_analyzer()
        
        # Get crypto-specific sentiment
        sentiment_result = analyzer.analyze_specific_crypto_sentiment(
            crypto_name=crypto_name,
            max_articles=max_articles
        )
        
        # Save to database
        sentiment_record = SentimentAnalysis(
            user_id=current_user.id,
            news_source=f"crypto_analysis_{crypto_name}",
            sentiment_score=sentiment_result['sentiment_score'],
            sentiment_label=sentiment_result['overall_sentiment'],
            confidence=sentiment_result['confidence'],
            news_text=f"Sentiment analysis for {crypto_name}"
        )
        
        db.add(sentiment_record)
        db.commit()
        
        return {
            "crypto_name": crypto_name,
            "overall_sentiment": sentiment_result['overall_sentiment'],
            "confidence": sentiment_result['confidence'],
            "sentiment_score": sentiment_result['sentiment_score'],
            "analysis_date": sentiment_result['analysis_date'],
            "articles_analyzed": sentiment_result.get('articles_analyzed', [])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Crypto sentiment analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crypto sentiment analysis failed: {str(e)}"
        )

@router.get("/history", response_model=List[SentimentHistory])
async def get_sentiment_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sentiment analysis history for the current user"""
    try:
        sentiment_history = db.query(SentimentAnalysis).filter(
            SentimentAnalysis.user_id == current_user.id
        ).order_by(
            SentimentAnalysis.analysis_date.desc()
        ).limit(limit).all()
        
        return [
            SentimentHistory(
                id=sentiment.id,
                news_source=sentiment.news_source,
                sentiment_score=sentiment.sentiment_score,
                sentiment_label=sentiment.sentiment_label,
                confidence=sentiment.confidence,
                analysis_date=sentiment.analysis_date.isoformat()
            )
            for sentiment in sentiment_history
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sentiment history: {str(e)}"
        )

@router.get("/trends")
async def get_sentiment_trends(
    days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """Get sentiment trends over time"""
    try:
        if days < 1 or days > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days must be between 1 and 30"
            )
        
        # Get sentiment analyzer
        analyzer = get_sentiment_analyzer()
        
        # Get trends (mock implementation)
        trends = analyzer.get_sentiment_trends(days=days)
        
        return trends
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment trends error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sentiment trends: {str(e)}"
        )

@router.get("/model-info", response_model=ModelInfo)
async def get_model_info():
    """Get sentiment analysis model information"""
    try:
        analyzer = get_sentiment_analyzer()
        info = analyzer.get_model_info()
        
        return ModelInfo(
            model_name=info.get('model_name', 'Unknown'),
            device=info.get('device', 'cpu'),
            max_length=info.get('max_length', 512),
            supports_batch=info.get('supports_batch', False),
            model_type=info.get('model_type', 'FinBERT')
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model info: {str(e)}"
        )

@router.get("/stats")
async def get_sentiment_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sentiment analysis statistics for the current user"""
    try:
        # Get total analyses
        total_analyses = db.query(SentimentAnalysis).filter(
            SentimentAnalysis.user_id == current_user.id
        ).count()
        
        # Get sentiment distribution
        sentiment_dist = db.query(
            SentimentAnalysis.sentiment_label,
            db.func.count(SentimentAnalysis.id).label('count'),
            db.func.avg(SentimentAnalysis.confidence).label('avg_confidence')
        ).filter(
            SentimentAnalysis.user_id == current_user.id
        ).group_by(
            SentimentAnalysis.sentiment_label
        ).all()
        
        # Get recent analyses
        recent_analyses = db.query(SentimentAnalysis).filter(
            SentimentAnalysis.user_id == current_user.id
        ).order_by(
            SentimentAnalysis.analysis_date.desc()
        ).limit(5).all()
        
        return {
            "total_analyses": total_analyses,
            "sentiment_distribution": [
                {
                    "label": dist.sentiment_label,
                    "count": dist.count,
                    "average_confidence": round(dist.avg_confidence, 3)
                }
                for dist in sentiment_dist
            ],
            "recent_analyses": [
                {
                    "source": analysis.news_source,
                    "sentiment": analysis.sentiment_label,
                    "confidence": analysis.confidence,
                    "date": analysis.analysis_date.isoformat()
                }
                for analysis in recent_analyses
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sentiment stats: {str(e)}"
        )
