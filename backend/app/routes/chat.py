"""
Chat routes for the Crypto AI Chatbot
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db
from models import User, ChatHistory
from auth import get_current_user
from ml.rag_nlp import get_chatbot
from utils import generate_session_id, sanitize_input

router = APIRouter()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    session_id: str
    timestamp: str
    sources: List[dict] = []

class ChatHistoryResponse(BaseModel):
    id: int
    user_message: str
    bot_response: str
    message_type: str
    created_at: str

class ChatSession(BaseModel):
    session_id: str
    created_at: str
    message_count: int

@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the chatbot"""
    try:
        # Sanitize input
        sanitized_message = sanitize_input(chat_message.message)
        if not sanitized_message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Generate or use existing session ID
        session_id = chat_message.session_id or generate_session_id()
        
        # Get chatbot instance
        chatbot = get_chatbot()
        
        # Generate response using RAG
        rag_response = chatbot.generate_response(sanitized_message)
        
        # Save chat history
        chat_history = ChatHistory(
            user_id=current_user.id,
            session_id=session_id,
            user_message=sanitized_message,
            bot_response=rag_response['response'],
            message_type="general"
        )
        
        db.add(chat_history)
        db.commit()
        db.refresh(chat_history)
        
        return ChatResponse(
            response=rag_response['response'],
            confidence=rag_response['confidence'],
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            sources=rag_response.get('sources', [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )

@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for the current user"""
    try:
        query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)
        
        if session_id:
            query = query.filter(ChatHistory.session_id == session_id)
        
        chat_history = query.order_by(ChatHistory.created_at.desc()).limit(limit).all()
        
        return [
            ChatHistoryResponse(
                id=chat.id,
                user_message=chat.user_message,
                bot_response=chat.bot_response,
                message_type=chat.message_type,
                created_at=chat.created_at.isoformat()
            )
            for chat in chat_history
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )

@router.get("/sessions", response_model=List[ChatSession])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for the current user"""
    try:
        # Get unique sessions with message counts
        sessions = db.query(
            ChatHistory.session_id,
            ChatHistory.created_at,
            db.func.count(ChatHistory.id).label('message_count')
        ).filter(
            ChatHistory.user_id == current_user.id
        ).group_by(
            ChatHistory.session_id,
            ChatHistory.created_at
        ).order_by(
            ChatHistory.created_at.desc()
        ).all()
        
        return [
            ChatSession(
                session_id=session.session_id,
                created_at=session.created_at.isoformat(),
                message_count=session.message_count
            )
            for session in sessions
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat sessions: {str(e)}"
        )

@router.delete("/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific chat session"""
    try:
        # Delete all messages in the session
        deleted_count = db.query(ChatHistory).filter(
            ChatHistory.user_id == current_user.id,
            ChatHistory.session_id == session_id
        ).delete()
        
        db.commit()
        
        return {"message": f"Deleted {deleted_count} messages from session {session_id}"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )

@router.get("/supported-cryptocurrencies")
async def get_supported_cryptocurrencies():
    """Get list of supported cryptocurrencies"""
    try:
        chatbot = get_chatbot()
        cryptocurrencies = chatbot.get_supported_cryptocurrencies()
        
        return {
            "supported_cryptocurrencies": cryptocurrencies,
            "count": len(cryptocurrencies)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported cryptocurrencies: {str(e)}"
        )

@router.get("/chatbot-info")
async def get_chatbot_info():
    """Get chatbot information and capabilities"""
    try:
        chatbot = get_chatbot()
        info = chatbot.get_model_info()
        
        return {
            "model_name": info.get('model_name', 'Unknown'),
            "index_size": info.get('index_size', 0),
            "data_size": info.get('data_size', 0),
            "supported_cryptocurrencies": info.get('supported_cryptocurrencies', 0),
            "capabilities": [
                "Cryptocurrency price information",
                "Market cap and volume data",
                "Price change analysis",
                "General cryptocurrency knowledge",
                "Trading insights"
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatbot info: {str(e)}"
        )
