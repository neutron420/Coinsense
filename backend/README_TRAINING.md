# CoinSense Model Training - Complete Guide

## 🚀 Quick Start

Your CoinSense platform is now ready for model training! Here's everything you need to know:

### Available Models
1. **LSTM Price Prediction** - Predicts cryptocurrency prices using historical data
2. **Sentiment Analysis** - Analyzes news sentiment using FinBERT
3. **RAG Chatbot** - Provides intelligent responses about cryptocurrencies

### Available Datasets
- **23 Individual Cryptocurrency Datasets** (`datasets/coins_datasets/`)
  - Bitcoin, Ethereum, Cardano, Solana, and 19 others
  - Historical price data from 2013-2024
  - Columns: Date, Open, High, Low, Close, Volume, Marketcap

- **2 General Market Datasets** (`datasets/crypto_datasets/`)
  - Cryptocurrency_Dataset_2021.csv
  - Cryptocurrency_Dataset_2023.csv
  - Market-wide cryptocurrency data

## 🎯 Training Options

### Option 1: Quick Start (Recommended for Beginners)
```bash
cd backend
python quick_train.py --action train-all --quick
```

### Option 2: Full Training Pipeline
```bash
cd backend
python quick_train.py --action full-pipeline
```

### Option 3: Advanced Training
```bash
cd backend
python train_models.py --model all --epochs 150 --batch-size 64
```

## 📋 Step-by-Step Training Instructions

### Step 1: Install Dependencies
```bash
pip install torch torchvision torchaudio
pip install transformers sentence-transformers faiss-cpu
pip install scikit-learn pandas numpy requests joblib matplotlib seaborn
```

### Step 2: Choose Your Training Method

#### Method A: Quick Training (5-10 minutes)
```bash
cd backend
python quick_train.py --action train-all --quick
```

#### Method B: Comprehensive Training (30-60 minutes)
```bash
cd backend
python train_models.py --model all --epochs 100 --batch-size 32
```

#### Method C: Individual Model Training
```bash
# Train LSTM for Bitcoin only
python train_models.py --model lstm --coin Bitcoin --epochs 150

# Train sentiment analysis
python train_models.py --model sentiment

# Train RAG chatbot
python train_models.py --model rag --rebuild-index
```

### Step 3: Evaluate Your Models
```bash
# Quick evaluation
python quick_train.py --action evaluate

# Comprehensive evaluation
python evaluate_models.py --model all --visualize --report
```

## 📊 What Gets Created

### Trained Models Directory (`trained_models/`)
```
trained_models/
├── lstm_bitcoin_model.pth          # LSTM model weights
├── lstm_bitcoin_scaler.pkl         # Data normalization scaler
├── lstm_ethereum_model.pth         # Additional LSTM models...
├── rag_index.index                 # RAG search index
├── rag_data.json                   # RAG knowledge base
└── training_results.json           # Training summary
```

### Evaluation Results (`evaluation_results/`)
```
evaluation_results/
├── lstm_bitcoin_evaluation.json     # Detailed LSTM metrics
├── sentiment_evaluation.json        # Sentiment analysis results
├── rag_evaluation.json             # RAG performance metrics
├── evaluation_summary.json          # Comprehensive summary
├── performance_report.md            # Human-readable report
└── lstm_bitcoin_performance.png    # Performance visualizations
```

## 🔧 Training Parameters Explained

### LSTM Model Parameters
- **epochs**: Number of training iterations (default: 100, quick: 50)
- **batch_size**: Training batch size (default: 32)
- **learning_rate**: Initial learning rate (default: 0.001)
- **sequence_length**: Days to look back (fixed: 60)

### Sentiment Analysis
- **model**: FinBERT (ProsusAI/finbert)
- **api_key**: NewsAPI key (optional, uses mock data if not provided)
- **max_length**: 512 tokens per text

### RAG Chatbot
- **embedding_model**: all-MiniLM-L6-v2
- **index_type**: FAISS IndexFlatIP
- **rebuild_index**: Whether to rebuild from datasets

## 📈 Performance Metrics

### LSTM Models
- **RMSE**: Root Mean Square Error (lower is better)
- **MAE**: Mean Absolute Error (lower is better)
- **MAPE**: Mean Absolute Percentage Error (lower is better)
- **R² Score**: Coefficient of determination (higher is better)
- **Directional Accuracy**: Correct price direction predictions (higher is better)

### Sentiment Analysis
- **Confidence**: Model confidence in predictions (0-1)
- **Response Time**: Processing speed in seconds
- **Sentiment Distribution**: Positive/Negative/Neutral percentages

### RAG Chatbot
- **Response Time**: Time to generate responses
- **Confidence**: Confidence in retrieved information
- **Source Count**: Number of knowledge sources used

## 🎮 Usage Examples

### Training Specific Cryptocurrencies
```bash
# Train LSTM for specific coins
python train_models.py --model lstm --coin Bitcoin --epochs 200
python train_models.py --model lstm --coin Ethereum --epochs 150

# Train multiple coins
python train_models.py --model lstm --coin Cardano --epochs 100
python train_models.py --model lstm --coin Solana --epochs 100
```

### Custom Training Configuration
```python
from train_models import ModelTrainer

trainer = ModelTrainer()

# Custom LSTM training
result = trainer.train_lstm_model(
    coin_symbol="Bitcoin",
    epochs=300,
    batch_size=64,
    learning_rate=0.0005
)

# Evaluate performance
evaluator = ModelEvaluator()
evaluation = evaluator.evaluate_lstm_model("Bitcoin", test_days=30)
```

### Batch Training Script
```bash
#!/bin/bash
# train_multiple_coins.sh

coins=("Bitcoin" "Ethereum" "Cardano" "Solana" "Polkadot")

for coin in "${coins[@]}"; do
    echo "Training LSTM for $coin"
    python train_models.py --model lstm --coin "$coin" --epochs 100
done
```

## 🔍 Model Evaluation

### Quick Evaluation
```bash
python evaluate_models.py --model lstm --coin Bitcoin
python evaluate_models.py --model sentiment
python evaluate_models.py --model rag
```

### Comprehensive Evaluation
```bash
python evaluate_models.py --model all --visualize --report
```

### Performance Visualization
```bash
python evaluate_models.py --model lstm --coin Bitcoin --visualize
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. CUDA/GPU Issues
```bash
# Force CPU usage
export CUDA_VISIBLE_DEVICES=""
python train_models.py --model all
```

#### 2. Memory Issues
```bash
# Reduce batch size
python train_models.py --model lstm --batch-size 16
```

#### 3. Dataset Not Found
```bash
# Check dataset structure
ls -la datasets/coins_datasets/
ls -la datasets/crypto_datasets/
```

#### 4. Model Loading Errors
```bash
# Rebuild from scratch
rm -rf trained_models/
python train_models.py --model all
```

#### 5. Dependencies Missing
```bash
# Install all required packages
pip install -r requirements.txt
pip install torch transformers sentence-transformers faiss-cpu
```

## 📚 Advanced Usage

### Custom Model Training
```python
# Advanced training with custom parameters
from train_models import ModelTrainer

trainer = ModelTrainer()

# Train with different configurations
configs = [
    {"epochs": 100, "batch_size": 32, "learning_rate": 0.001},
    {"epochs": 200, "batch_size": 64, "learning_rate": 0.0005},
    {"epochs": 150, "batch_size": 16, "learning_rate": 0.002}
]

for i, config in enumerate(configs):
    result = trainer.train_lstm_model("Bitcoin", **config)
    print(f"Config {i+1} results: {result['metrics']}")
```

### Model Comparison
```python
# Compare different models
from evaluate_models import ModelEvaluator

evaluator = ModelEvaluator()

# Evaluate multiple coins
coins = ["Bitcoin", "Ethereum", "Cardano"]
results = {}

for coin in coins:
    try:
        result = evaluator.evaluate_lstm_model(coin)
        results[coin] = result['metrics']
    except Exception as e:
        print(f"Failed to evaluate {coin}: {e}")

# Compare results
for coin, metrics in results.items():
    print(f"{coin}: RMSE={metrics['rmse']:.4f}, MAPE={metrics['mape']:.2f}%")
```

## 🎯 Best Practices

### Training Recommendations
1. **Start with Quick Training**: Use `--quick` flag for initial testing
2. **Monitor Performance**: Always evaluate models after training
3. **Regular Retraining**: Retrain models every 30 days with new data
4. **Parameter Tuning**: Experiment with different epochs and learning rates
5. **Backup Models**: Keep copies of well-performing models

### Performance Optimization
1. **Use GPU**: Enable CUDA for faster training (if available)
2. **Batch Size**: Increase batch size for better GPU utilization
3. **Data Quality**: Ensure clean, complete datasets
4. **Feature Engineering**: Consider adding technical indicators
5. **Ensemble Methods**: Train multiple models and combine predictions

## 📞 Support and Next Steps

### After Training
1. **Test Models**: Use evaluation scripts to verify performance
2. **Deploy Models**: Integrate trained models into your API
3. **Monitor Performance**: Track model accuracy over time
4. **Retrain Regularly**: Update models with new data
5. **Scale Up**: Train models for additional cryptocurrencies

### Getting Help
- Check `training.log` for detailed error messages
- Review evaluation results in `evaluation_results/`
- Ensure all dependencies are properly installed
- Verify dataset structure and format

### Integration with API
Once trained, your models are ready to be used in your FastAPI endpoints:
- LSTM models for price predictions
- Sentiment analysis for news analysis
- RAG chatbot for intelligent responses

## 🎉 Congratulations!

You now have everything you need to train and evaluate your CoinSense models:

✅ **Training Scripts**: `train_models.py`, `quick_train.py`  
✅ **Evaluation Tools**: `evaluate_models.py`  
✅ **Comprehensive Guide**: `TRAINING_GUIDE.md`  
✅ **Datasets**: 23 cryptocurrency datasets ready for training  
✅ **Model Architectures**: LSTM, FinBERT, RAG chatbot  

**Happy Training!** 🚀

Start with the quick training option and gradually move to more advanced configurations as you become comfortable with the process.
