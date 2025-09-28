#!/usr/bin/env python3
"""
Model Evaluation and Testing Utilities for CoinSense
Comprehensive testing and evaluation tools for all trained models
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import argparse
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from ml.lstm_model import CryptoPricePredictor, load_crypto_data
from ml.sentiment_model import CryptoNewsSentimentAnalyzer
from ml.rag_nlp import CryptoRAGChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Comprehensive model evaluation and testing utilities"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(__file__)
        self.models_dir = os.path.join(self.base_dir, 'trained_models')
        self.results_dir = os.path.join(self.base_dir, 'evaluation_results')
        
        # Create results directory
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Evaluation results
        self.evaluation_results = {}
    
    def evaluate_lstm_model(self, coin_symbol: str, test_days: int = 30) -> Dict:
        """Comprehensive evaluation of LSTM model"""
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
            
            if len(df) < test_days + 60:  # Need at least 60 days for sequence + test days
                raise ValueError(f"Insufficient data for evaluation: {len(df)} days")
            
            # Split data for evaluation
            train_data = df.iloc[:-test_days]
            test_data = df.iloc[-test_days:]
            
            # Make predictions
            predictions = predictor.predict_price(train_data, days_ahead=test_days)
            predicted_prices = predictions['predictions']
            
            # Get actual prices
            actual_prices = test_data['Close'].values
            
            # Calculate metrics
            mse = mean_squared_error(actual_prices, predicted_prices)
            mae = mean_absolute_error(actual_prices, predicted_prices)
            rmse = np.sqrt(mse)
            
            # Calculate percentage errors
            mape = np.mean(np.abs((actual_prices - predicted_prices) / actual_prices)) * 100
            
            # Calculate directional accuracy
            actual_direction = np.diff(actual_prices) > 0
            predicted_direction = np.diff(predicted_prices) > 0
            directional_accuracy = np.mean(actual_direction == predicted_direction) * 100
            
            # Calculate R-squared
            r2 = r2_score(actual_prices, predicted_prices)
            
            # Price volatility analysis
            price_volatility = np.std(actual_prices) / np.mean(actual_prices)
            
            # Create evaluation results
            evaluation = {
                'coin': coin_symbol,
                'model_type': 'LSTM',
                'test_period': f"{test_days} days",
                'metrics': {
                    'mse': float(mse),
                    'mae': float(mae),
                    'rmse': float(rmse),
                    'mape': float(mape),
                    'r2_score': float(r2),
                    'directional_accuracy': float(directional_accuracy)
                },
                'data_info': {
                    'total_data_points': len(df),
                    'training_data_points': len(train_data),
                    'test_data_points': len(test_data),
                    'price_volatility': float(price_volatility),
                    'current_price': float(df['Close'].iloc[-1])
                },
                'predictions': {
                    'actual_prices': actual_prices.tolist(),
                    'predicted_prices': predicted_prices,
                    'prediction_confidence': predictions['confidence'],
                    'prediction_date': predictions['prediction_date']
                },
                'model_info': predictor.get_model_info(),
                'evaluation_date': datetime.now().isoformat()
            }
            
            # Save detailed results
            self._save_evaluation_results(f'lstm_{coin_symbol.lower()}', evaluation)
            
            logger.info(f"LSTM evaluation completed for {coin_symbol}")
            logger.info(f"RMSE: {rmse:.4f}, MAE: {mae:.4f}, MAPE: {mape:.2f}%")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"LSTM evaluation failed for {coin_symbol}: {e}")
            raise
    
    def evaluate_sentiment_model(self, test_articles: List[Dict] = None) -> Dict:
        """Evaluate sentiment analysis model"""
        try:
            logger.info("Evaluating sentiment analysis model")
            
            # Initialize analyzer
            analyzer = CryptoNewsSentimentAnalyzer()
            
            # Use provided test articles or generate mock data
            if test_articles is None:
                test_articles = analyzer._get_mock_news()
            
            # Analyze sentiment
            sentiment_results = analyzer.analyze_news_sentiment(test_articles)
            
            # Calculate evaluation metrics
            total_articles = len(sentiment_results)
            positive_count = sum(1 for r in sentiment_results if r.label == 'positive')
            negative_count = sum(1 for r in sentiment_results if r.label == 'negative')
            neutral_count = sum(1 for r in sentiment_results if r.label == 'neutral')
            
            avg_confidence = np.mean([r.confidence for r in sentiment_results])
            
            # Test response time
            start_time = datetime.now()
            analyzer.analyze_sentiment("Bitcoin reaches new all-time high")
            response_time = (datetime.now() - start_time).total_seconds()
            
            evaluation = {
                'model_type': 'Sentiment Analysis',
                'test_articles': total_articles,
                'metrics': {
                    'positive_predictions': positive_count,
                    'negative_predictions': negative_count,
                    'neutral_predictions': neutral_count,
                    'average_confidence': float(avg_confidence),
                    'response_time_seconds': float(response_time)
                },
                'sentiment_distribution': {
                    'positive_percentage': (positive_count / total_articles) * 100,
                    'negative_percentage': (negative_count / total_articles) * 100,
                    'neutral_percentage': (neutral_count / total_articles) * 100
                },
                'sample_results': [
                    {
                        'text': result.text[:100] + "..." if len(result.text) > 100 else result.text,
                        'label': result.label,
                        'confidence': result.confidence,
                        'source': result.source
                    }
                    for result in sentiment_results[:5]  # Show first 5 results
                ],
                'model_info': analyzer.get_model_info(),
                'evaluation_date': datetime.now().isoformat()
            }
            
            # Save results
            self._save_evaluation_results('sentiment', evaluation)
            
            logger.info("Sentiment analysis evaluation completed")
            logger.info(f"Average confidence: {avg_confidence:.3f}, Response time: {response_time:.3f}s")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Sentiment evaluation failed: {e}")
            raise
    
    def evaluate_rag_model(self, test_queries: List[str] = None) -> Dict:
        """Evaluate RAG chatbot model"""
        try:
            logger.info("Evaluating RAG chatbot model")
            
            # Initialize chatbot
            index_path = os.path.join(self.models_dir, 'rag_index.index')
            data_path = os.path.join(self.models_dir, 'rag_data.json')
            
            if not os.path.exists(index_path):
                raise ValueError("RAG index not found. Please train the RAG model first.")
            
            chatbot = CryptoRAGChatbot(index_path=index_path, data_path=data_path)
            
            # Default test queries
            if test_queries is None:
                test_queries = [
                    "What is Bitcoin?",
                    "What is the current price of Ethereum?",
                    "Which cryptocurrency has the highest market cap?",
                    "Tell me about Dogecoin",
                    "What are the top performing cryptocurrencies?",
                    "Explain cryptocurrency trading volume",
                    "What is market capitalization?",
                    "How does cryptocurrency work?",
                    "What is the difference between Bitcoin and Ethereum?",
                    "Which crypto has the most trading activity?"
                ]
            
            # Test queries
            query_results = []
            total_response_time = 0
            total_confidence = 0
            
            for query in test_queries:
                start_time = datetime.now()
                response = chatbot.generate_response(query)
                response_time = (datetime.now() - start_time).total_seconds()
                
                query_results.append({
                    'query': query,
                    'response': response['response'],
                    'confidence': response['confidence'],
                    'response_time': response_time,
                    'sources_count': len(response.get('sources', []))
                })
                
                total_response_time += response_time
                total_confidence += response['confidence']
            
            # Calculate metrics
            avg_response_time = total_response_time / len(test_queries)
            avg_confidence = total_confidence / len(test_queries)
            
            # Test search functionality
            search_results = chatbot.search("Bitcoin price", top_k=5)
            
            evaluation = {
                'model_type': 'RAG Chatbot',
                'test_queries': len(test_queries),
                'metrics': {
                    'average_response_time': float(avg_response_time),
                    'average_confidence': float(avg_confidence),
                    'total_sources_used': sum(r['sources_count'] for r in query_results)
                },
                'query_results': query_results,
                'search_test': {
                    'query': 'Bitcoin price',
                    'results_count': len(search_results),
                    'top_result_similarity': search_results[0]['similarity_score'] if search_results else 0
                },
                'model_info': chatbot.get_model_info(),
                'supported_cryptocurrencies': chatbot.get_supported_cryptocurrencies()[:10],  # First 10
                'evaluation_date': datetime.now().isoformat()
            }
            
            # Save results
            self._save_evaluation_results('rag', evaluation)
            
            logger.info("RAG chatbot evaluation completed")
            logger.info(f"Average response time: {avg_response_time:.3f}s, Average confidence: {avg_confidence:.3f}")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"RAG evaluation failed: {e}")
            raise
    
    def evaluate_all_models(self, test_coins: List[str] = None) -> Dict:
        """Evaluate all trained models"""
        logger.info("Starting comprehensive model evaluation")
        
        if test_coins is None:
            test_coins = ["Bitcoin", "Ethereum", "Cardano"]
        
        all_results = {
            'lstm_evaluations': {},
            'sentiment_evaluation': {},
            'rag_evaluation': {},
            'evaluation_summary': {}
        }
        
        # Evaluate LSTM models
        for coin in test_coins:
            try:
                lstm_result = self.evaluate_lstm_model(coin)
                all_results['lstm_evaluations'][coin] = lstm_result
            except Exception as e:
                logger.error(f"LSTM evaluation failed for {coin}: {e}")
                all_results['lstm_evaluations'][coin] = {'error': str(e)}
        
        # Evaluate sentiment model
        try:
            sentiment_result = self.evaluate_sentiment_model()
            all_results['sentiment_evaluation'] = sentiment_result
        except Exception as e:
            logger.error(f"Sentiment evaluation failed: {e}")
            all_results['sentiment_evaluation'] = {'error': str(e)}
        
        # Evaluate RAG model
        try:
            rag_result = self.evaluate_rag_model()
            all_results['rag_evaluation'] = rag_result
        except Exception as e:
            logger.error(f"RAG evaluation failed: {e}")
            all_results['rag_evaluation'] = {'error': str(e)}
        
        # Create evaluation summary
        all_results['evaluation_summary'] = {
            'total_models_evaluated': len([r for r in all_results.values() if isinstance(r, dict) and 'error' not in r]),
            'lstm_models_evaluated': len([r for r in all_results['lstm_evaluations'].values() if 'error' not in r]),
            'evaluation_completed': datetime.now().isoformat(),
            'results_directory': self.results_dir
        }
        
        # Save comprehensive results
        summary_path = os.path.join(self.results_dir, 'evaluation_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        logger.info("All model evaluations completed")
        logger.info(f"Evaluation results saved to: {summary_path}")
        
        return all_results
    
    def create_performance_visualizations(self, coin_symbol: str):
        """Create performance visualizations for LSTM model"""
        try:
            logger.info(f"Creating visualizations for {coin_symbol}")
            
            # Load evaluation results
            result_file = os.path.join(self.results_dir, f'lstm_{coin_symbol.lower()}_evaluation.json')
            if not os.path.exists(result_file):
                raise ValueError(f"Evaluation results not found for {coin_symbol}")
            
            with open(result_file, 'r') as f:
                evaluation = json.load(f)
            
            predictions = evaluation['predictions']
            actual_prices = predictions['actual_prices']
            predicted_prices = predictions['predicted_prices']
            
            # Create plots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'LSTM Model Performance - {coin_symbol}', fontsize=16)
            
            # Plot 1: Actual vs Predicted Prices
            axes[0, 0].plot(actual_prices, label='Actual', marker='o')
            axes[0, 0].plot(predicted_prices, label='Predicted', marker='s')
            axes[0, 0].set_title('Actual vs Predicted Prices')
            axes[0, 0].set_xlabel('Days')
            axes[0, 0].set_ylabel('Price ($)')
            axes[0, 0].legend()
            axes[0, 0].grid(True)
            
            # Plot 2: Prediction Errors
            errors = np.array(actual_prices) - np.array(predicted_prices)
            axes[0, 1].plot(errors, marker='o', color='red')
            axes[0, 1].set_title('Prediction Errors')
            axes[0, 1].set_xlabel('Days')
            axes[0, 1].set_ylabel('Error ($)')
            axes[0, 1].grid(True)
            axes[0, 1].axhline(y=0, color='black', linestyle='--')
            
            # Plot 3: Error Distribution
            axes[1, 0].hist(errors, bins=10, alpha=0.7, color='skyblue')
            axes[1, 0].set_title('Error Distribution')
            axes[1, 0].set_xlabel('Error ($)')
            axes[1, 0].set_ylabel('Frequency')
            axes[1, 0].grid(True)
            
            # Plot 4: Scatter Plot
            axes[1, 1].scatter(actual_prices, predicted_prices, alpha=0.7)
            axes[1, 1].plot([min(actual_prices), max(actual_prices)], 
                           [min(actual_prices), max(actual_prices)], 'r--')
            axes[1, 1].set_title('Actual vs Predicted Scatter')
            axes[1, 1].set_xlabel('Actual Price ($)')
            axes[1, 1].set_ylabel('Predicted Price ($)')
            axes[1, 1].grid(True)
            
            plt.tight_layout()
            
            # Save plot
            plot_path = os.path.join(self.results_dir, f'lstm_{coin_symbol.lower()}_performance.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Visualizations saved to: {plot_path}")
            
        except Exception as e:
            logger.error(f"Visualization creation failed for {coin_symbol}: {e}")
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report"""
        try:
            logger.info("Generating performance report")
            
            # Load evaluation summary
            summary_path = os.path.join(self.results_dir, 'evaluation_summary.json')
            if not os.path.exists(summary_path):
                raise ValueError("Evaluation summary not found. Please run evaluations first.")
            
            with open(summary_path, 'r') as f:
                summary = json.load(f)
            
            # Generate report
            report = f"""
# CoinSense Model Performance Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- Total Models Evaluated: {summary['evaluation_summary']['total_models_evaluated']}
- LSTM Models Evaluated: {summary['evaluation_summary']['lstm_models_evaluated']}
- Evaluation Date: {summary['evaluation_summary']['evaluation_completed']}

## LSTM Price Prediction Models

"""
            
            # LSTM Results
            for coin, result in summary['lstm_evaluations'].items():
                if 'error' not in result:
                    metrics = result['metrics']
                    report += f"""
### {coin}
- **RMSE**: ${metrics['rmse']:.4f}
- **MAE**: ${metrics['mae']:.4f}
- **MAPE**: {metrics['mape']:.2f}%
- **R² Score**: {metrics['r2_score']:.4f}
- **Directional Accuracy**: {metrics['directional_accuracy']:.2f}%
- **Test Period**: {result['test_period']}
- **Price Volatility**: {result['data_info']['price_volatility']:.4f}

"""
                else:
                    report += f"""
### {coin}
- **Status**: Error - {result['error']}

"""
            
            # Sentiment Analysis Results
            if 'error' not in summary['sentiment_evaluation']:
                sent_metrics = summary['sentiment_evaluation']['metrics']
                report += f"""
## Sentiment Analysis Model
- **Average Confidence**: {sent_metrics['average_confidence']:.3f}
- **Response Time**: {sent_metrics['response_time_seconds']:.3f}s
- **Test Articles**: {summary['sentiment_evaluation']['test_articles']}
- **Sentiment Distribution**:
  - Positive: {summary['sentiment_evaluation']['sentiment_distribution']['positive_percentage']:.1f}%
  - Negative: {summary['sentiment_evaluation']['sentiment_distribution']['negative_percentage']:.1f}%
  - Neutral: {summary['sentiment_evaluation']['sentiment_distribution']['neutral_percentage']:.1f}%

"""
            else:
                report += f"""
## Sentiment Analysis Model
- **Status**: Error - {summary['sentiment_evaluation']['error']}

"""
            
            # RAG Model Results
            if 'error' not in summary['rag_evaluation']:
                rag_metrics = summary['rag_evaluation']['metrics']
                report += f"""
## RAG Chatbot Model
- **Average Response Time**: {rag_metrics['average_response_time']:.3f}s
- **Average Confidence**: {rag_metrics['average_confidence']:.3f}
- **Test Queries**: {summary['rag_evaluation']['test_queries']}
- **Total Sources Used**: {rag_metrics['total_sources_used']}
- **Supported Cryptocurrencies**: {len(summary['rag_evaluation']['supported_cryptocurrencies'])}

"""
            else:
                report += f"""
## RAG Chatbot Model
- **Status**: Error - {summary['rag_evaluation']['error']}

"""
            
            report += f"""
## Recommendations

### LSTM Models
- Monitor models with MAPE > 10% for potential retraining
- Consider ensemble methods for coins with high volatility
- Regular retraining recommended every 30 days

### Sentiment Analysis
- Model performs well with high confidence scores
- Consider fine-tuning on crypto-specific news data
- Monitor response times for production deployment

### RAG Chatbot
- Good response times and confidence levels
- Consider expanding knowledge base with more recent data
- Regular index updates recommended

## Files Generated
- Evaluation Results: {self.results_dir}/
- Performance Visualizations: Available for LSTM models
- Detailed JSON Results: evaluation_summary.json

---
Report generated by CoinSense Model Evaluator
"""
            
            # Save report
            report_path = os.path.join(self.results_dir, 'performance_report.md')
            with open(report_path, 'w') as f:
                f.write(report)
            
            logger.info(f"Performance report saved to: {report_path}")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise
    
    def _save_evaluation_results(self, model_name: str, results: Dict):
        """Save evaluation results to file"""
        result_path = os.path.join(self.results_dir, f'{model_name}_evaluation.json')
        with open(result_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Evaluation results saved to: {result_path}")

def main():
    """Main evaluation function"""
    parser = argparse.ArgumentParser(description='Evaluate CoinSense models')
    parser.add_argument('--model', choices=['lstm', 'sentiment', 'rag', 'all'], 
                       default='all', help='Model to evaluate')
    parser.add_argument('--coin', type=str, help='Specific coin for LSTM evaluation')
    parser.add_argument('--test-days', type=int, default=30, help='Test days for LSTM evaluation')
    parser.add_argument('--visualize', action='store_true', help='Create performance visualizations')
    parser.add_argument('--report', action='store_true', help='Generate performance report')
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = ModelEvaluator()
    
    try:
        if args.model == 'lstm':
            if args.coin:
                result = evaluator.evaluate_lstm_model(args.coin, args.test_days)
                print(f"LSTM evaluation completed for {args.coin}")
                print(f"RMSE: {result['metrics']['rmse']:.4f}")
                print(f"MAE: {result['metrics']['mae']:.4f}")
                print(f"MAPE: {result['metrics']['mape']:.2f}%")
            else:
                print("Please specify a coin for LSTM evaluation using --coin")
        
        elif args.model == 'sentiment':
            result = evaluator.evaluate_sentiment_model()
            print(f"Sentiment evaluation completed")
            print(f"Average confidence: {result['metrics']['average_confidence']:.3f}")
            print(f"Response time: {result['metrics']['response_time_seconds']:.3f}s")
        
        elif args.model == 'rag':
            result = evaluator.evaluate_rag_model()
            print(f"RAG evaluation completed")
            print(f"Average response time: {result['metrics']['average_response_time']:.3f}s")
            print(f"Average confidence: {result['metrics']['average_confidence']:.3f}")
        
        elif args.model == 'all':
            results = evaluator.evaluate_all_models()
            print(f"All model evaluations completed")
            print(f"Results saved to: {evaluator.results_dir}")
        
        # Create visualizations if requested
        if args.visualize and args.coin:
            evaluator.create_performance_visualizations(args.coin)
            print(f"Visualizations created for {args.coin}")
        
        # Generate report if requested
        if args.report:
            report = evaluator.generate_performance_report()
            print("Performance report generated")
    
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
