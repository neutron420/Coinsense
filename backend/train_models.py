

import os
import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from ml.lstm_model import CryptoPricePredictor, load_crypto_data
from ml.sentiment_model import CryptoNewsSentimentAnalyzer
from ml.rag_nlp import CryptoRAGChatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Comprehensive model trainer for all CoinSense models"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(__file__)
        # Go up one level from backend to reach the main project directory
        project_root = os.path.dirname(self.base_dir)
        self.datasets_dir = os.path.join(project_root, 'datasets')
        self.datasets_dir = os.path.abspath(self.datasets_dir)
        self.models_dir = os.path.join(self.base_dir, 'trained_models')
        
        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Training results
        self.training_results = {}
    
    def get_available_coins(self) -> List[str]:
        """Get list of available cryptocurrency datasets"""
        coins_dir = os.path.join(self.datasets_dir, 'coins_datasets')
        if not os.path.exists(coins_dir):
            logger.error(f"Coins dataset directory not found: {coins_dir}")
            return []
        
        coin_files = [f for f in os.listdir(coins_dir) if f.startswith('coin_') and f.endswith('.csv')]
        coins = [f.replace('coin_', '').replace('.csv', '') for f in coin_files]
        return sorted(coins)
    
    def train_lstm_model(self, coin_symbol: str, epochs: int = 100, batch_size: int = 32, learning_rate: float = 0.001) -> Dict:
        """Train LSTM model for a specific cryptocurrency"""
        try:
            logger.info(f"Starting LSTM training for {coin_symbol}")
            
            # Load data
            df = load_crypto_data(coin_symbol, days=1000)  # Use more data for training
            
            if df.empty:
                raise ValueError(f"No data found for {coin_symbol}")
            
            logger.info(f"Loaded {len(df)} records for {coin_symbol}")
            
            # Initialize predictor
            predictor = CryptoPricePredictor()
            
            # Train model
            metrics = predictor.train_model(
                df=df,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate
            )
            
            # Save model
            model_path = os.path.join(self.models_dir, f'lstm_{coin_symbol.lower()}_model.pth')
            scaler_path = os.path.join(self.models_dir, f'lstm_{coin_symbol.lower()}_scaler.pkl')
            
            predictor.save_model(model_path, scaler_path)
            
            # Store results
            result = {
                'coin': coin_symbol,
                'model_type': 'LSTM',
                'metrics': metrics,
                'model_path': model_path,
                'scaler_path': scaler_path,
                'training_date': datetime.now().isoformat(),
                'data_points': len(df)
            }
            
            self.training_results[f'lstm_{coin_symbol.lower()}'] = result
            
            logger.info(f"LSTM training completed for {coin_symbol}")
            logger.info(f"Final metrics: {metrics}")
            
            return result
            
        except Exception as e:
            logger.error(f"LSTM training failed for {coin_symbol}: {e}")
            raise
    
    def train_all_lstm_models(self, epochs: int = 100, batch_size: int = 32, learning_rate: float = 0.001) -> Dict:
        """Train LSTM models for all available cryptocurrencies"""
        logger.info("Starting LSTM training for all cryptocurrencies")
        
        available_coins = self.get_available_coins()
        if not available_coins:
            logger.error("No cryptocurrency datasets found")
            return {}
        
        results = {}
        successful_trains = 0
        
        for coin in available_coins:
            try:
                result = self.train_lstm_model(coin, epochs, batch_size, learning_rate)
                results[coin] = result
                successful_trains += 1
                logger.info(f"Successfully trained LSTM for {coin}")
                
            except Exception as e:
                logger.error(f"Failed to train LSTM for {coin}: {e}")
                results[coin] = {'error': str(e)}
        
        logger.info(f"LSTM training completed: {successful_trains}/{len(available_coins)} successful")
        return results
    
    def train_sentiment_model(self, api_key: str = None) -> Dict:
        """Train/Initialize sentiment analysis model"""
        try:
            logger.info("Initializing sentiment analysis model")
            
            # Initialize sentiment analyzer
            analyzer = CryptoNewsSentimentAnalyzer(api_key=api_key)
            
            # Test the model with sample data
            test_articles = analyzer._get_mock_news()
            sentiment_results = analyzer.analyze_news_sentiment(test_articles)
            
            # Get model info
            model_info = analyzer.get_model_info()
            
            result = {
                'model_type': 'Sentiment Analysis',
                'model_name': model_info['model_name'],
                'device': model_info['device'],
                'test_results': {
                    'articles_analyzed': len(sentiment_results),
                    'sample_sentiments': [r.label for r in sentiment_results]
                },
                'training_date': datetime.now().isoformat(),
                'status': 'initialized'
            }
            
            self.training_results['sentiment'] = result
            
            logger.info("Sentiment analysis model initialized successfully")
            return result
            
        except Exception as e:
            logger.error(f"Sentiment model initialization failed: {e}")
            raise
    
    def train_rag_model(self, rebuild_index: bool = True) -> Dict:
        """Train/Initialize RAG chatbot model"""
        try:
            logger.info("Initializing RAG chatbot model")
            
            # Set up paths
            index_path = os.path.join(self.models_dir, 'rag_index.index')
            data_path = os.path.join(self.models_dir, 'rag_data.json')
            
            # Initialize chatbot
            chatbot = CryptoRAGChatbot(
                index_path=index_path if not rebuild_index else None,
                data_path=data_path if not rebuild_index else None
            )
            
            if rebuild_index:
                # Build index from datasets
                dataset_dir = os.path.join(self.datasets_dir, 'crypto_datasets')
                chatbot.build_index_from_directory(dataset_dir)
                
                # Save the index
                chatbot.save_index(index_path, data_path)
            
            # Test the model
            test_query = "What is Bitcoin?"
            response = chatbot.generate_response(test_query)
            
            # Get model info
            model_info = chatbot.get_model_info()
            
            result = {
                'model_type': 'RAG Chatbot',
                'model_name': model_info['model_name'],
                'index_size': model_info['index_size'],
                'data_size': model_info['data_size'],
                'supported_cryptocurrencies': model_info['supported_cryptocurrencies'],
                'test_response': response,
                'index_path': index_path,
                'data_path': data_path,
                'training_date': datetime.now().isoformat(),
                'status': 'initialized'
            }
            
            self.training_results['rag'] = result
            
            logger.info("RAG chatbot model initialized successfully")
            return result
            
        except Exception as e:
            logger.error(f"RAG model initialization failed: {e}")
            raise
    
    def train_all_models(self, 
                        lstm_epochs: int = 100, 
                        lstm_batch_size: int = 32, 
                        lstm_learning_rate: float = 0.001,
                        sentiment_api_key: str = None,
                        rebuild_rag_index: bool = True) -> Dict:
        """Train all models"""
        logger.info("Starting comprehensive model training")
        
        all_results = {
            'lstm_models': {},
            'sentiment_model': {},
            'rag_model': {},
            'training_summary': {}
        }
        
        # Train LSTM models
        try:
            lstm_results = self.train_all_lstm_models(lstm_epochs, lstm_batch_size, lstm_learning_rate)
            all_results['lstm_models'] = lstm_results
        except Exception as e:
            logger.error(f"LSTM training failed: {e}")
            all_results['lstm_models'] = {'error': str(e)}
        
        # Train sentiment model
        try:
            sentiment_result = self.train_sentiment_model(sentiment_api_key)
            all_results['sentiment_model'] = sentiment_result
        except Exception as e:
            logger.error(f"Sentiment model training failed: {e}")
            all_results['sentiment_model'] = {'error': str(e)}
        
        # Train RAG model
        try:
            rag_result = self.train_rag_model(rebuild_rag_index)
            all_results['rag_model'] = rag_result
        except Exception as e:
            logger.error(f"RAG model training failed: {e}")
            all_results['rag_model'] = {'error': str(e)}
        
        # Create training summary
        all_results['training_summary'] = {
            'total_models_trained': len([r for r in all_results.values() if isinstance(r, dict) and 'error' not in r]),
            'lstm_models_trained': len([r for r in all_results['lstm_models'].values() if 'error' not in r]),
            'training_completed': datetime.now().isoformat(),
            'models_directory': self.models_dir
        }
        
        # Save training results
        results_path = os.path.join(self.models_dir, 'training_results.json')
        with open(results_path, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        logger.info("All model training completed")
        logger.info(f"Training results saved to: {results_path}")
        
        return all_results
    
    def evaluate_model_performance(self, coin_symbol: str) -> Dict:
        """Evaluate performance of a trained LSTM model"""
        try:
            logger.info(f"Evaluating LSTM model for {coin_symbol}")
            
            # Load model
            model_path = os.path.join(self.models_dir, f'lstm_{coin_symbol.lower()}_model.pth')
            scaler_path = os.path.join(self.models_dir, f'lstm_{coin_symbol.lower()}_scaler.pkl')
            
            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                raise ValueError(f"Model files not found for {coin_symbol}")
            
            predictor = CryptoPricePredictor(model_path, scaler_path)
            
            # Load test data
            df = load_crypto_data(coin_symbol, days=365)
            
            # Make predictions
            predictions = predictor.predict_price(df, days_ahead=7)
            
            # Calculate evaluation metrics
            recent_prices = df['Close'].tail(30).values
            price_volatility = np.std(recent_prices) / np.mean(recent_prices)
            
            evaluation = {
                'coin': coin_symbol,
                'model_type': 'LSTM',
                'predictions': predictions,
                'price_volatility': float(price_volatility),
                'evaluation_date': datetime.now().isoformat(),
                'model_info': predictor.get_model_info()
            }
            
            logger.info(f"Model evaluation completed for {coin_symbol}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Model evaluation failed for {coin_symbol}: {e}")
            raise

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train CoinSense models')
    parser.add_argument('--model', choices=['lstm', 'sentiment', 'rag', 'all'], 
                       default='all', help='Model to train')
    parser.add_argument('--coin', type=str, help='Specific coin for LSTM training')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs for LSTM')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size for LSTM')
    parser.add_argument('--learning-rate', type=float, default=0.001, help='Learning rate for LSTM')
    parser.add_argument('--api-key', type=str, help='NewsAPI key for sentiment analysis')
    parser.add_argument('--rebuild-index', action='store_true', help='Rebuild RAG index')
    parser.add_argument('--evaluate', action='store_true', help='Evaluate model performance')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    try:
        if args.model == 'lstm':
            if args.coin:
                result = trainer.train_lstm_model(args.coin, args.epochs, args.batch_size, args.learning_rate)
                print(f"LSTM training completed for {args.coin}")
                print(f"Results: {json.dumps(result, indent=2, default=str)}")
            else:
                results = trainer.train_all_lstm_models(args.epochs, args.batch_size, args.learning_rate)
                print(f"LSTM training completed for all coins")
                print(f"Results: {json.dumps(results, indent=2, default=str)}")
        
        elif args.model == 'sentiment':
            result = trainer.train_sentiment_model(args.api_key)
            print(f"Sentiment model training completed")
            print(f"Results: {json.dumps(result, indent=2, default=str)}")
        
        elif args.model == 'rag':
            result = trainer.train_rag_model(args.rebuild_index)
            print(f"RAG model training completed")
            print(f"Results: {json.dumps(result, indent=2, default=str)}")
        
        elif args.model == 'all':
            results = trainer.train_all_models(
                lstm_epochs=args.epochs,
                lstm_batch_size=args.batch_size,
                lstm_learning_rate=args.learning_rate,
                sentiment_api_key=args.api_key,
                rebuild_rag_index=args.rebuild_index
            )
            print(f"All model training completed")
            print(f"Results: {json.dumps(results, indent=2, default=str)}")
        
        # Evaluate if requested
        if args.evaluate and args.coin:
            evaluation = trainer.evaluate_model_performance(args.coin)
            print(f"Model evaluation completed for {args.coin}")
            print(f"Evaluation: {json.dumps(evaluation, indent=2, default=str)}")
    
    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
