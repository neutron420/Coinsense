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
    # Added optional URL here too, though not strictly required by the dataclass itself for this change
    url: Optional[str] = None

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
                device=0 if torch.cuda.is_available() else -1,
                truncation=True # Added truncation
            )

            logger.info("FinBERT model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading FinBERT model: {e}")
            raise

    def fetch_crypto_news(self, query: str = "cryptocurrency", max_articles: int = 10) -> List[Dict]:
        """Fetch cryptocurrency news from NewsAPI"""
        try:
            # Check if api_key is None or the placeholder value
            if not self.api_key or "your-newsapi-key" in self.api_key:
                logger.warning("No valid NewsAPI key provided, using mock data")
                return self._get_mock_news()

            url = "https://newsapi.org/v2/everything"
            # Ensure max_articles is within NewsAPI limits (1-100)
            page_size = max(1, min(100, max_articles))
            params = {
                'q': query,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': page_size
            }
            logger.info(f"Fetching news with query: '{query}', pageSize: {page_size}")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            data = response.json()
            articles = data.get('articles', [])

            # Process articles
            processed_articles = []
            for article in articles:
                 # Basic check for essential fields
                if article.get('title') and (article.get('description') or article.get('content')):
                    processed_articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''), # Content might be partial
                        'url': article.get('url', ''), # Get the URL
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'publishedAt': article.get('publishedAt', ''),
                        'urlToImage': article.get('urlToImage', '')
                    })

            logger.info(f"Fetched {len(processed_articles)} relevant news articles for query '{query}'")
            return processed_articles

        except requests.exceptions.RequestException as req_err:
             logger.error(f"NewsAPI request failed: {req_err}")
             return self._get_mock_news() # Fallback on network/API errors
        except Exception as e:
            logger.error(f"Unexpected error fetching news: {e}", exc_info=True)
            return self._get_mock_news() # Fallback for other errors

    def _get_mock_news(self) -> List[Dict]:
        """Get mock news data for testing"""
        logger.debug("Using mock news data.")
        return [
            {
                'title': 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
                'description': 'Major corporations continue to invest in Bitcoin, driving prices to record levels.',
                'content': 'Bitcoin has reached a new all-time high...',
                'url': 'https://example.com/mock-btc-news', # Mock URL
                'source': 'Mock CryptoNews',
                'publishedAt': datetime.now().isoformat()
            },
            {
                'title': 'Ethereum Network Upgrade Shows Promising Results',
                'description': 'The latest Ethereum network upgrade has improved transaction speeds and reduced fees.',
                'content': 'Ethereums recent network upgrade shows improvements...',
                'url': 'https://example.com/mock-eth-news', # Mock URL
                'source': 'Mock EthereumNews',
                'publishedAt': (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                'title': 'Regulatory Concerns Impact Altcoin Markets',
                'description': 'Recent regulatory announcements have caused uncertainty in the altcoin market.',
                'content': 'Regulatory announcements cause uncertainty...',
                'url': 'https://example.com/mock-reg-news', # Mock URL
                'source': 'Mock RegulatoryNews',
                'publishedAt': (datetime.now() - timedelta(hours=4)).isoformat()
            }
        ]

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        if not isinstance(text, str): # Handle potential non-string input
            return ""

        # Clean text
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) # Remove URLs
        text = re.sub(r'\s+', ' ', text).strip() # Consolidate whitespace and strip ends

        # Truncation is handled by the pipeline, so no need to do it manually here.
        # logger.debug(f"Preprocessed text (first 50): {text[:50]}")
        return text

    # Changed return type to Dict for consistency
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of a single text, returns Dict"""
        try:
            processed_text = self.preprocess_text(text)
            if not processed_text:
                return {'label': 'neutral', 'score': 0.5, 'confidence': 0.5} # Return neutral dict

            # Get sentiment prediction
            result = self.pipeline(processed_text)
            # logger.debug(f"Pipeline raw result: {result}")


            # Extract results safely
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                sentiment_data = result[0]
                label = sentiment_data.get('label', 'neutral').lower()
                score = sentiment_data.get('score', 0.5) # Use 0.5 as neutral default

                # Map FinBERT labels
                mapped_label = 'neutral'
                if 'positive' in label:
                    mapped_label = 'positive'
                elif 'negative' in label:
                    mapped_label = 'negative'

                # Return a dictionary
                return {
                    'label': mapped_label,
                    'score': float(score),
                    'confidence': float(score) # Use score as confidence for now
                    # 'text': processed_text # Optionally include text
                }
            else:
                logger.warning(f"Unexpected result format from sentiment pipeline: {result}")
                return {'label': 'neutral', 'score': 0.5, 'confidence': 0.5}

        except Exception as e:
            logger.error(f"Sentiment analysis failed for text: '{text[:50]}...': {e}", exc_info=True)
            return {'label': 'neutral', 'score': 0.5, 'confidence': 0.5} # Return neutral dict on error

    # Changed return type annotation to List[Dict]
    def analyze_news_sentiment(self, articles: List[Dict]) -> List[Dict]:
        """Analyze sentiment of multiple news articles, returns list of Dicts"""
        results = []
        texts_to_analyze = []
        original_indices = [] # Keep track of original article index

        # Prepare texts, skipping empty ones
        for i, article in enumerate(articles):
            text = f"{article.get('title', '')} {article.get('description', '')}"
            processed = self.preprocess_text(text)
            if processed: # Only analyze non-empty text
                 texts_to_analyze.append(processed)
                 original_indices.append(i)

        if not texts_to_analyze:
             logger.warning("No valid text found in articles to analyze.")
             return []

        try:
            # Attempt batch analysis
            batch_results = self.pipeline(texts_to_analyze)
            # logger.debug(f"Batch analysis results: {batch_results}")

            # Process batch results back into the final list
            temp_results = {} # Use dict to map back easily
            for i, result_data in enumerate(batch_results):
                 original_index = original_indices[i]
                 label = result_data.get('label', 'neutral').lower()
                 score = result_data.get('score', 0.5)

                 mapped_label = 'neutral'
                 if 'positive' in label: mapped_label = 'positive'
                 elif 'negative' in label: mapped_label = 'negative'

                 article_info = articles[original_index] # Get original article data
                 temp_results[original_index] = {
                     'label': mapped_label,
                     'score': float(score),
                     'confidence': float(score),
                     'source': article_info.get('source', 'Unknown'),
                     'url': article_info.get('url', ''), # Include URL
                     'title': article_info.get('title', '') # Include Title
                 }

            # Build final results list in original order
            for i in range(len(articles)):
                 if i in temp_results:
                     results.append(temp_results[i])
                 # else: Optionally handle articles that had no text or failed analysis

        except Exception as e:
            logger.error(f"Batch sentiment analysis failed, falling back to individual: {e}", exc_info=False)
            # Fallback to individual analysis
            results = [] # Clear any partial batch results
            for article in articles:
                text_to_analyze = f"{article.get('title', '')} {article.get('description', '')}"
                # Use analyze_sentiment which returns a Dict
                sentiment_result_dict = self.analyze_sentiment(text_to_analyze)

                # Add extra info
                sentiment_result_dict['source'] = article.get('source', 'Unknown')
                sentiment_result_dict['url'] = article.get('url', '') # *** INCLUDE URL ***
                sentiment_result_dict['title'] = article.get('title', '') # *** INCLUDE TITLE ***

                results.append(sentiment_result_dict)

        # logger.debug(f"Finished analyzing sentiments for {len(results)} articles.")
        return results


    def get_market_sentiment(self, query: str = "cryptocurrency", max_articles: int = 10) -> Dict:
        """Get overall market sentiment from news"""
        try:
            articles = self.fetch_crypto_news(query, max_articles)

            if not articles:
                 logger.warning(f"No articles fetched for query '{query}'. Returning neutral.")
                 # Return structure consistent with success case but empty/neutral
                 return {
                     'overall_sentiment': 'neutral', 'confidence': 0.0,
                     'positive_count': 0, 'negative_count': 0, 'neutral_count': 0,
                     'total_articles': 0, 'sentiment_score': 0.0,
                     'analysis_date': datetime.now().isoformat(), 'articles_analyzed': []
                 }

            # Analyze sentiment (returns list of dicts)
            sentiment_results = self.analyze_news_sentiment(articles) # List[Dict]

            if not sentiment_results:
                 logger.warning(f"Sentiment analysis yielded no results for query '{query}'. Returning neutral.")
                 return {
                     'overall_sentiment': 'neutral', 'confidence': 0.0,
                     'positive_count': 0, 'negative_count': 0, 'neutral_count': 0,
                     'total_articles': 0, 'sentiment_score': 0.0,
                     'analysis_date': datetime.now().isoformat(), 'articles_analyzed': []
                 }


            # Calculate counts and scores from the list of dicts
            positive_count = sum(1 for r in sentiment_results if r['label'] == 'positive')
            negative_count = sum(1 for r in sentiment_results if r['label'] == 'negative')
            total_analyzed = len(sentiment_results)
            neutral_count = total_analyzed - positive_count - negative_count

            sentiment_scores = []
            for result in sentiment_results:
                if result['label'] == 'positive':
                    sentiment_scores.append(result['score']) # score is 0-1
                elif result['label'] == 'negative':
                    sentiment_scores.append(-result['score']) # score is 0-1, make it negative
                else:
                    sentiment_scores.append(0.0)

            avg_sentiment_score = np.mean(sentiment_scores) if sentiment_scores else 0.0
            avg_sentiment_score = float(np.clip(avg_sentiment_score, -1.0, 1.0)) # Ensure score is float and clamped


            # Determine overall sentiment label
            overall_sentiment = 'neutral'
            if positive_count > negative_count and positive_count >= neutral_count: # Prioritize positive if tied with neutral
                overall_sentiment = 'positive'
            elif negative_count > positive_count and negative_count > neutral_count: # Only negative if strictly dominant
                overall_sentiment = 'negative'
            # Stays neutral otherwise

            # Calculate confidence
            confidence = 0.0
            if total_analyzed > 0:
                max_count = max(positive_count, negative_count, neutral_count)
                confidence = max_count / total_analyzed
                # Optional: Modulate confidence by score magnitude?
                # confidence = confidence * abs(avg_sentiment_score)


            # Prepare articles_analyzed list for the response, ensuring URL is included
            # sentiment_results already contains 'title', 'sentiment', 'confidence', 'source', 'url'
            articles_analyzed_response = [
                 {
                     'title': r.get('title', 'N/A'),
                     'sentiment': r['label'],
                     'confidence': r['confidence'],
                     'source': r.get('source', 'Unknown'),
                     'url': r.get('url', '') # *** ENSURE URL IS PASSED ***
                 }
                 for r in sentiment_results # Iterate through the list of dicts
             ]


            return {
                'overall_sentiment': overall_sentiment,
                'confidence': float(confidence),
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_articles': total_analyzed, # Use count of analyzed articles
                'sentiment_score': avg_sentiment_score,
                'analysis_date': datetime.now().isoformat(),
                'articles_analyzed': articles_analyzed_response # Use the correctly formatted list
            }

        except Exception as e:
            logger.error(f"Market sentiment analysis failed for query '{query}': {e}", exc_info=True)
            return {
                'overall_sentiment': 'neutral', 'confidence': 0.0,
                'positive_count': 0, 'negative_count': 0, 'neutral_count': 0,
                'total_articles': 0, 'sentiment_score': 0.0,
                'analysis_date': datetime.now().isoformat(),
                'articles_analyzed': [],
                'error': f"An internal error occurred: {str(e)}"
            }

    def analyze_specific_crypto_sentiment(self, crypto_name: str, max_articles: int = 10) -> Dict:
        """Analyze sentiment for a specific cryptocurrency"""
        # Use a query more specific to the crypto
        query = f'"{crypto_name}" cryptocurrency OR "{crypto_name}" crypto OR "{crypto_name}" blockchain'
        logger.info(f"Analyzing specific crypto sentiment for '{crypto_name}' with query: '{query}'")
        return self.get_market_sentiment(query, max_articles)

    def get_sentiment_trends(self, days: int = 7) -> Dict:
        """Get sentiment trends over time (mock implementation)"""
        logger.warning("get_sentiment_trends called - returning mock data.")
        return {
            'trend_period': f"{days} days",
            'status': 'mock_implementation', # Indicate it's mock
            'average_sentiment': 'neutral',
            'trend_direction': 'stable',
            'note': 'Historical trend data storage and retrieval not implemented.'
        }

    def get_model_info(self) -> Dict:
        """Get model information"""
        # Basic info, avoid accessing potentially non-existent attributes if model loading failed
        info = {
            'model_name': self.model_name,
            'device': str(self.device),
        }
        try:
             if self.model and hasattr(self.model, 'config'):
                 config = self.model.config
                 info['max_length'] = getattr(config, 'max_position_embeddings', 512)
                 info['model_type'] = getattr(config, 'model_type', 'unknown').replace('ForSequenceClassification', '')
        except Exception as e:
            logger.warning(f"Could not get detailed model config info: {e}")
            info['error'] = 'Could not retrieve detailed config'
        return info

# --- Global Instance Management ---
sentiment_analyzer_instance: Optional[CryptoNewsSentimentAnalyzer] = None

def get_sentiment_analyzer(api_key: Optional[str] = None) -> CryptoNewsSentimentAnalyzer:
    """Get or create global sentiment analyzer instance, update API key if provided."""
    global sentiment_analyzer_instance
    if sentiment_analyzer_instance is None:
        logger.info("Initializing global Sentiment Analyzer instance.")
        # Try to get API key from environment or config if not passed directly
        # Example: api_key = api_key or os.getenv('NEWS_API_KEY')
        sentiment_analyzer_instance = CryptoNewsSentimentAnalyzer(api_key=api_key)
    # Update API key if a new, valid key is provided
    elif api_key and api_key != "your-newsapi-key" and sentiment_analyzer_instance.api_key != api_key:
        logger.info("Updating API key for existing Sentiment Analyzer instance.")
        sentiment_analyzer_instance.api_key = api_key
    # If no key provided now, but instance exists, keep existing key
    elif not api_key and sentiment_analyzer_instance.api_key:
         pass # Keep the existing key
     # If no key provided now and instance has no valid key, update it if possible
    elif not api_key and (not sentiment_analyzer_instance.api_key or "your-newsapi-key" in sentiment_analyzer_instance.api_key):
         # Try to update from env/config again?
         # Example: updated_key = os.getenv('NEWS_API_KEY')
         # if updated_key and updated_key != "your-newsapi-key":
         #    logger.info("Setting API key from environment during retrieval.")
         #    sentiment_analyzer_instance.api_key = updated_key
         pass # Or just leave it as is

    # Ensure an instance is returned, even if initialization failed somehow (though it should raise)
    if sentiment_analyzer_instance is None:
        raise RuntimeError("Failed to create or retrieve Sentiment Analyzer instance.")

    return sentiment_analyzer_instance

# Example Initialization (e.g., in your main FastAPI app setup)
# from app.config import settings # Assuming you have a config module
# initial_api_key = settings.news_api_key
# try:
#     get_sentiment_analyzer(api_key=initial_api_key)
#     logger.info("Sentiment Analyzer initialized successfully.")
# except Exception as e:
#     logger.error(f"Failed to initialize Sentiment Analyzer: {e}", exc_info=True)