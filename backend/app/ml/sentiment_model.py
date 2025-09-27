"""
FinBERT Sentiment Analysis for Cryptocurrency News
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import requests
import json
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime, timedelta
import re
import numpy as np
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    label: str
    score: float
    confidence: float
    text: str
    source: str
    timestamp: datetime

class CryptoNewsSentimentAnalyzer:
    """Cryptocurrency news sentiment analysis using FinBERT"""
    
    def __init__(self, model_name: str = "ProsusAI/finbert", api_key: str = None):
        self.model_name = model_name
        self.api_key = api_key
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load FinBERT model and tokenizer"""
        try:
            logger.info(f"Loading FinBERT model: {self.model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # Move to device
            self.model.to(self.device)
            self.model.eval()
            
            # Create pipeline
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("FinBERT model loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading FinBERT model: {e}")
            raise
    
    def fetch_crypto_news(self, query: str = "cryptocurrency", max_articles: int = 10) -> List[Dict]:
        """Fetch cryptocurrency news from NewsAPI"""
        try:
            if not self.api_key:
                logger.warning("No NewsAPI key provided, using mock data")
                return self._get_mock_news()
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': max_articles
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Process articles
            processed_articles = []
            for article in articles:
                processed_articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'publishedAt': article.get('publishedAt', ''),
                    'urlToImage': article.get('urlToImage', '')
                })
            
            logger.info(f"Fetched {len(processed_articles)} news articles")
            return processed_articles
        
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return self._get_mock_news()
    
    def _get_mock_news(self) -> List[Dict]:
        """Get mock news data for testing"""
        return [
            {
                'title': 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
                'description': 'Major corporations continue to invest in Bitcoin, driving prices to record levels.',
                'content': 'Bitcoin has reached a new all-time high as institutional investors continue to show strong interest in the cryptocurrency. Several major corporations have announced Bitcoin purchases, contributing to the positive market sentiment.',
                'source': 'CryptoNews',
                'publishedAt': datetime.now().isoformat()
            },
            {
                'title': 'Ethereum Network Upgrade Shows Promising Results',
                'description': 'The latest Ethereum network upgrade has improved transaction speeds and reduced fees.',
                'content': 'Ethereum\'s recent network upgrade has shown significant improvements in transaction processing speeds and has successfully reduced gas fees for users. This development has been met with positive reception from the community.',
                'source': 'EthereumNews',
                'publishedAt': (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                'title': 'Regulatory Concerns Impact Altcoin Markets',
                'description': 'Recent regulatory announcements have caused uncertainty in the altcoin market.',
                'content': 'Recent regulatory announcements from various governments have created uncertainty in the cryptocurrency market, particularly affecting smaller altcoins. Investors are showing caution as they await clearer regulatory guidance.',
                'source': 'RegulatoryNews',
                'publishedAt': (datetime.now() - timedelta(hours=4)).isoformat()
            }
        ]
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        if not text:
            return ""
        
        # Clean text
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Truncate if too long (FinBERT has token limits)
        if len(text) > 512:
            text = text[:512]
        
        return text
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text"""
        try:
            if not text or not text.strip():
                return SentimentResult(
                    label="neutral",
                    score=0.0,
                    confidence=0.0,
                    text=text,
                    source="",
                    timestamp=datetime.now()
                )
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            if not processed_text:
                return SentimentResult(
                    label="neutral",
                    score=0.0,
                    confidence=0.0,
                    text=text,
                    source="",
                    timestamp=datetime.now()
                )
            
            # Get sentiment prediction
            result = self.pipeline(processed_text)
            
            # Extract results
            if isinstance(result, list) and len(result) > 0:
                sentiment_data = result[0]
                label = sentiment_data['label'].lower()
                score = sentiment_data['score']
                
                # Map FinBERT labels to our labels
                if 'positive' in label:
                    mapped_label = 'positive'
                elif 'negative' in label:
                    mapped_label = 'negative'
                else:
                    mapped_label = 'neutral'
                
                return SentimentResult(
                    label=mapped_label,
                    score=score,
                    confidence=score,
                    text=processed_text,
                    source="",
                    timestamp=datetime.now()
                )
            else:
                return SentimentResult(
                    label="neutral",
                    score=0.0,
                    confidence=0.0,
                    text=processed_text,
                    source="",
                    timestamp=datetime.now()
                )
        
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return SentimentResult(
                label="neutral",
                score=0.0,
                confidence=0.0,
                text=text,
                source="",
                timestamp=datetime.now()
            )
    
    def analyze_news_sentiment(self, articles: List[Dict]) -> List[SentimentResult]:
        """Analyze sentiment of multiple news articles"""
        results = []
        
        for article in articles:
            # Combine title and description for analysis
            text_to_analyze = f"{article.get('title', '')} {article.get('description', '')}"
            
            # Analyze sentiment
            sentiment_result = self.analyze_sentiment(text_to_analyze)
            sentiment_result.source = article.get('source', 'Unknown')
            sentiment_result.text = text_to_analyze
            
            results.append(sentiment_result)
        
        return results
    
    def get_market_sentiment(self, query: str = "cryptocurrency", max_articles: int = 10) -> Dict:
        """Get overall market sentiment from news"""
        try:
            # Fetch news
            articles = self.fetch_crypto_news(query, max_articles)
            
            if not articles:
                return {
                    'overall_sentiment': 'neutral',
                    'confidence': 0.0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'total_articles': 0,
                    'sentiment_score': 0.0,
                    'analysis_date': datetime.now().isoformat()
                }
            
            # Analyze sentiment
            sentiment_results = self.analyze_news_sentiment(articles)
            
            # Calculate overall sentiment
            positive_count = sum(1 for r in sentiment_results if r.label == 'positive')
            negative_count = sum(1 for r in sentiment_results if r.label == 'negative')
            neutral_count = sum(1 for r in sentiment_results if r.label == 'neutral')
            
            # Calculate sentiment score (-1 to 1)
            sentiment_scores = []
            for result in sentiment_results:
                if result.label == 'positive':
                    sentiment_scores.append(result.score)
                elif result.label == 'negative':
                    sentiment_scores.append(-result.score)
                else:
                    sentiment_scores.append(0.0)
            
            avg_sentiment_score = np.mean(sentiment_scores) if sentiment_scores else 0.0
            
            # Determine overall sentiment
            if positive_count > negative_count and positive_count > neutral_count:
                overall_sentiment = 'positive'
            elif negative_count > positive_count and negative_count > neutral_count:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
            
            # Calculate confidence
            total_articles = len(sentiment_results)
            max_count = max(positive_count, negative_count, neutral_count)
            confidence = max_count / total_articles if total_articles > 0 else 0.0
            
            return {
                'overall_sentiment': overall_sentiment,
                'confidence': float(confidence),
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_articles': total_articles,
                'sentiment_score': float(avg_sentiment_score),
                'analysis_date': datetime.now().isoformat(),
                'articles_analyzed': [
                    {
                        'title': article.get('title', ''),
                        'sentiment': result.label,
                        'confidence': result.confidence,
                        'source': result.source
                    }
                    for article, result in zip(articles, sentiment_results)
                ]
            }
        
        except Exception as e:
            logger.error(f"Market sentiment analysis error: {e}")
            return {
                'overall_sentiment': 'neutral',
                'confidence': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0,
                'sentiment_score': 0.0,
                'analysis_date': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def analyze_specific_crypto_sentiment(self, crypto_name: str, max_articles: int = 10) -> Dict:
        """Analyze sentiment for a specific cryptocurrency"""
        query = f"{crypto_name} cryptocurrency"
        return self.get_market_sentiment(query, max_articles)
    
    def get_sentiment_trends(self, days: int = 7) -> Dict:
        """Get sentiment trends over time (mock implementation)"""
        # This would typically involve storing historical sentiment data
        # For now, we'll return a mock trend
        return {
            'trend_period': f"{days} days",
            'average_sentiment': 'positive',
            'trend_direction': 'improving',
            'volatility': 'medium',
            'key_events': [
                'Institutional adoption increased',
                'Regulatory clarity improved',
                'Market confidence strengthened'
            ]
        }
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'device': str(self.device),
            'max_length': 512,
            'supports_batch': True,
            'model_type': 'FinBERT'
        }

# Global sentiment analyzer instance
sentiment_analyzer = None

def get_sentiment_analyzer() -> CryptoNewsSentimentAnalyzer:
    """Get or create global sentiment analyzer instance"""
    global sentiment_analyzer
    if sentiment_analyzer is None:
        sentiment_analyzer = CryptoNewsSentimentAnalyzer()
    return sentiment_analyzer
