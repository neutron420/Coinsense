"""
Price prediction routes for the Crypto AI Chatbot
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from database import get_db
from models import User, Prediction
from auth import get_current_user
from ml.lstm_model import get_predictor, load_crypto_data
from utils import validate_crypto_symbol, normalize_crypto_symbol, format_currency, calculate_confidence_level
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models
class PredictionRequest(BaseModel):
    symbol: str
    days_ahead: int = 1

class PredictionResponse(BaseModel):
    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    confidence_level: str
    prediction_date: str
    days_ahead: int

class PredictionHistory(BaseModel):
    id: int
    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    prediction_date: str
    actual_price: Optional[float] = None
    accuracy: Optional[float] = None

class ModelInfo(BaseModel):
    model_type: str
    input_size: int
    hidden_size: int
    num_layers: int
    sequence_length: int
    total_parameters: int
    trainable_parameters: int
    device: str

@router.post("/predict", response_model=PredictionResponse)
async def predict_price(
    prediction_request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predict cryptocurrency price using LSTM model"""
    try:
        # Validate and normalize symbol
        symbol = normalize_crypto_symbol(prediction_request.symbol)
        if not validate_crypto_symbol(symbol):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid cryptocurrency symbol: {prediction_request.symbol}"
            )
        
        # Validate days_ahead
        if prediction_request.days_ahead < 1 or prediction_request.days_ahead > 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days ahead must be between 1 and 7"
            )
        
        # Get predictor instance
        predictor = get_predictor()

        # Ensure a model is loaded for this symbol if available
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            trained_dir = os.path.join(project_root, 'trained_models')
            coin_key = symbol.lower()
            model_file = f"lstm_{coin_key}_model.pth"
            scaler_file = f"lstm_{coin_key}_scaler.pkl"
            model_path = os.path.join(trained_dir, model_file)
            scaler_path = os.path.join(trained_dir, scaler_file)

            if os.path.exists(model_path) and os.path.exists(scaler_path):
                predictor.load_model(model_path)
                predictor.load_scaler(scaler_path)
            else:
                # If specific model not found, try a generic bitcoin model as fallback
                btc_model = os.path.join(trained_dir, 'lstm_bitcoin_model.pth')
                btc_scaler = os.path.join(trained_dir, 'lstm_bitcoin_scaler.pkl')
                if os.path.exists(btc_model) and os.path.exists(btc_scaler):
                    predictor.load_model(btc_model)
                    predictor.load_scaler(btc_scaler)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="No trained model available. Please train a model first."
                    )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Model load failed: {str(e)}"
            )
        
        # Load cryptocurrency data
        try:
            df = load_crypto_data(symbol, days=365)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not load data for {symbol}: {str(e)}"
            )
        
        # Make prediction
        try:
            prediction_result = predictor.predict_price(df, days_ahead=prediction_request.days_ahead)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Prediction failed: {str(e)}"
            )
        
        # Extract prediction data
        current_price = prediction_result['current_price']
        predicted_price = prediction_result['predictions'][0]  # First day prediction
        confidence = prediction_result['confidence']
        
        # Save prediction to database
        prediction_record = Prediction(
            user_id=current_user.id,
            cryptocurrency=symbol,
            current_price=current_price,
            predicted_price=predicted_price,
            confidence_score=confidence
        )
        
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)
        
        return PredictionResponse(
            symbol=symbol,
            current_price=current_price,
            predicted_price=predicted_price,
            confidence=confidence,
            confidence_level=calculate_confidence_level(confidence),
            prediction_date=prediction_result['prediction_date'],
            days_ahead=prediction_request.days_ahead
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@router.get("/history", response_model=List[PredictionHistory])
async def get_prediction_history(
    symbol: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get prediction history for the current user"""
    try:
        query = db.query(Prediction).filter(Prediction.user_id == current_user.id)
        
        if symbol:
            normalized_symbol = normalize_crypto_symbol(symbol)
            query = query.filter(Prediction.cryptocurrency == normalized_symbol)
        
        predictions = query.order_by(Prediction.prediction_date.desc()).limit(limit).all()
        
        return [
            PredictionHistory(
                id=pred.id,
                symbol=pred.cryptocurrency,
                current_price=pred.current_price,
                predicted_price=pred.predicted_price,
                confidence=pred.confidence_score,
                prediction_date=pred.prediction_date.isoformat(),
                actual_price=pred.actual_price,
                accuracy=pred.accuracy
            )
            for pred in predictions
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve prediction history: {str(e)}"
        )

@router.get("/supported-symbols")
async def get_supported_symbols():
    """Get list of supported cryptocurrency symbols"""
    try:
        # List of supported symbols based on available datasets
        supported_symbols = [
            "BTC", "ETH", "ADA", "DOT", "LINK", "LTC", "XRP", "DOGE", 
            "SOL", "MATIC", "BNB", "USDT", "USDC", "WBTC", "UNI", "AAVE",
            "ATOM", "CRO", "EOS", "IOTA", "XMR", "NEM", "XLM", "TRX"
        ]
        
        return {
            "supported_symbols": supported_symbols,
            "count": len(supported_symbols),
            "note": "Symbols are case-insensitive"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported symbols: {str(e)}"
        )

@router.get("/model-info", response_model=ModelInfo)
async def get_model_info():
    """Get LSTM model information"""
    try:
        predictor = get_predictor()
        info = predictor.get_model_info()
        
        return ModelInfo(
            model_type=info.get('model_type', 'LSTM'),
            input_size=info.get('input_size', 1),
            hidden_size=info.get('hidden_size', 50),
            num_layers=info.get('num_layers', 2),
            sequence_length=info.get('sequence_length', 60),
            total_parameters=info.get('total_parameters', 0),
            trainable_parameters=info.get('trainable_parameters', 0),
            device=info.get('device', 'cpu')
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model info: {str(e)}"
        )

@router.post("/train-model")
async def train_model(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train LSTM model for a specific cryptocurrency (Admin only)"""
    try:
        # For now, allow all users to train models
        # In production, you might want to restrict this to admin users
        
        symbol = normalize_crypto_symbol(symbol)
        if not validate_crypto_symbol(symbol):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid cryptocurrency symbol: {symbol}"
            )
        
        # Load data
        df = load_crypto_data(symbol, days=365)
        
        # Get predictor and train
        predictor = get_predictor()
        metrics = predictor.train_model(df, epochs=50, batch_size=32)
        
        # Save model
        model_path = f"./models/lstm_{symbol.lower()}_model.pth"
        scaler_path = f"./models/lstm_{symbol.lower()}_scaler.pkl"
        predictor.save_model(model_path, scaler_path)
        
        return {
            "message": f"Model trained successfully for {symbol}",
            "metrics": metrics,
            "model_path": model_path,
            "scaler_path": scaler_path
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model training error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )

@router.get("/prediction-stats")
async def get_prediction_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get prediction statistics for the current user"""
    try:
        # Get total predictions
        total_predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).count()
        
        # Get predictions by symbol
        symbol_stats = db.query(
            Prediction.cryptocurrency,
            db.func.count(Prediction.id).label('count'),
            db.func.avg(Prediction.confidence_score).label('avg_confidence')
        ).filter(
            Prediction.user_id == current_user.id
        ).group_by(
            Prediction.cryptocurrency
        ).all()
        
        # Get recent predictions
        recent_predictions = db.query(Prediction).filter(
            Prediction.user_id == current_user.id
        ).order_by(
            Prediction.prediction_date.desc()
        ).limit(5).all()
        
        return {
            "total_predictions": total_predictions,
            "symbol_statistics": [
                {
                    "symbol": stat.cryptocurrency,
                    "count": stat.count,
                    "average_confidence": round(stat.avg_confidence, 3)
                }
                for stat in symbol_stats
            ],
            "recent_predictions": [
                {
                    "symbol": pred.cryptocurrency,
                    "predicted_price": pred.predicted_price,
                    "confidence": pred.confidence_score,
                    "date": pred.prediction_date.isoformat()
                }
                for pred in recent_predictions
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prediction stats: {str(e)}"
        )
