#!/usr/bin/env python3
"""
Quick Start Training Script for CoinSense
Simplified training script for easy model training
"""

import os
import sys
import argparse
import logging

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from train_models import ModelTrainer
from evaluate_models import ModelEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def quick_train_all():
    """Quick training for all models with default settings"""
    logger.info("Starting quick training for all models...")
    
    trainer = ModelTrainer()
    
    # Train all models with conservative settings for quick training
    results = trainer.train_all_models(
        lstm_epochs=50,  # Reduced for quick training
        lstm_batch_size=32,
        lstm_learning_rate=0.001,
        sentiment_api_key=None,  # Use mock data
        rebuild_rag_index=True
    )
    
    logger.info("Quick training completed!")
    return results

def quick_train_lstm_only():
    """Quick training for LSTM models only"""
    logger.info("Starting quick LSTM training...")
    
    trainer = ModelTrainer()
    
    # Train LSTM for major cryptocurrencies only
    major_coins = ["Bitcoin", "Ethereum", "Cardano", "Solana"]
    results = {}
    
    for coin in major_coins:
        try:
            result = trainer.train_lstm_model(coin, epochs=50, batch_size=32, learning_rate=0.001)
            results[coin] = result
            logger.info(f"✓ Trained LSTM for {coin}")
        except Exception as e:
            logger.error(f"✗ Failed to train LSTM for {coin}: {e}")
            results[coin] = {'error': str(e)}
    
    logger.info("Quick LSTM training completed!")
    return results

def quick_evaluate():
    """Quick evaluation of trained models"""
    logger.info("Starting quick evaluation...")
    
    evaluator = ModelEvaluator()
    
    # Evaluate major cryptocurrencies
    test_coins = ["Bitcoin", "Ethereum"]
    results = evaluator.evaluate_all_models(test_coins)
    
    logger.info("Quick evaluation completed!")
    return results

def main():
    """Main function with simplified options"""
    parser = argparse.ArgumentParser(description='Quick Start CoinSense Training')
    parser.add_argument('--action', choices=['train-all', 'train-lstm', 'evaluate', 'full-pipeline'], 
                       default='train-all', help='Action to perform')
    parser.add_argument('--quick', action='store_true', help='Use quick settings (fewer epochs)')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'train-all':
            if args.quick:
                results = quick_train_all()
            else:
                trainer = ModelTrainer()
                results = trainer.train_all_models()
            print("✓ All models trained successfully!")
            
        elif args.action == 'train-lstm':
            if args.quick:
                results = quick_train_lstm_only()
            else:
                trainer = ModelTrainer()
                results = trainer.train_all_lstm_models()
            print("✓ LSTM models trained successfully!")
            
        elif args.action == 'evaluate':
            results = quick_evaluate()
            print("✓ Model evaluation completed!")
            
        elif args.action == 'full-pipeline':
            logger.info("Running full training and evaluation pipeline...")
            
            # Train all models
            trainer = ModelTrainer()
            train_results = trainer.train_all_models()
            print("✓ Training completed!")
            
            # Evaluate models
            evaluator = ModelEvaluator()
            eval_results = evaluator.evaluate_all_models()
            print("✓ Evaluation completed!")
            
            # Generate report
            report = evaluator.generate_performance_report()
            print("✓ Performance report generated!")
            
            print("\n🎉 Full pipeline completed successfully!")
            print(f"📁 Results saved in: {trainer.models_dir}")
            print(f"📊 Evaluation results: {evaluator.results_dir}")
        
        print("\nNext steps:")
        print("1. Check the trained_models/ directory for your trained models")
        print("2. Run evaluation to test model performance")
        print("3. Integrate models into your API endpoints")
        print("4. Monitor model performance over time")
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure all dependencies are installed")
        print("2. Check that dataset files exist in datasets/ directory")
        print("3. Ensure you have sufficient disk space")
        print("4. Check training.log for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    main()
