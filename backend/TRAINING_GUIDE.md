# CoinSense Model Training Guide

This comprehensive guide explains how to train all the machine learning models in your CoinSense cryptocurrency analysis platform.

## Overview

Your CoinSense platform includes three main ML models:

1. **LSTM Price Prediction Model** - Predicts cryptocurrency prices using historical data
2. **Sentiment Analysis Model** - Analyzes news sentiment using FinBERT
3. **RAG Chatbot Model** - Provides intelligent responses about cryptocurrencies

## Prerequisites

### Required Dependencies
Make sure you have all required packages installed:

```bash
pip install torch torchvision torchaudio
pip install transformers
pip install sentence-transformers
pip install faiss-cpu  # or faiss-gpu for GPU support
pip install scikit-learn
pip install pandas numpy
pip install requests
pip install joblib
```

### Dataset Structure
Your datasets are organized as follows:
```
datasets/
├── coins_datasets/          # Historical price data for individual coins
│   ├── coin_Bitcoin.csv
│   ├── coin_Ethereum.csv
│   └── ... (23 total coins)
└── crypto_datasets/         # General cryptocurrency market data
    ├── Cryptocurrency_Dataset_2021.csv
    └── Cryptocurrency_Dataset_2023.csv
```

## Training Methods

### Method 1: Using the Training Script (Recommended)

The `train_models.py` script provides a comprehensive training solution:

#### Train All Models
```bash
cd backend
python train_models.py --model all
```

#### Train Specific Models

**LSTM Models:**
```bash
# Train LSTM for all cryptocurrencies
python train_models.py --model lstm --epochs 150 --batch-size 64 --learning-rate 0.001

# Train LSTM for specific cryptocurrency
python train_models.py --model lstm --coin Bitcoin --epochs 200
```

**Sentiment Analysis Model:**
```bash
# Train with NewsAPI key (optional)
python train_models.py --model sentiment --api-key YOUR_NEWSAPI_KEY

# Train without API key (uses mock data)
python train_models.py --model sentiment
```

**RAG Chatbot Model:**
```bash
# Train and rebuild index
python train_models.py --model rag --rebuild-index

# Train using existing index
python train_models.py --model rag
```

#### Evaluate Model Performance
```bash
python train_models.py --model lstm --coin Bitcoin --evaluate
```

### Method 2: Programmatic Training

You can also train models programmatically in Python:

```python
from train_models import ModelTrainer

# Initialize trainer
trainer = ModelTrainer()

# Train all models
results = trainer.train_all_models(
    lstm_epochs=100,
    lstm_batch_size=32,
    lstm_learning_rate=0.001,
    sentiment_api_key="your_api_key",  # Optional
    rebuild_rag_index=True
)

# Train specific LSTM model
btc_result = trainer.train_lstm_model("Bitcoin", epochs=150)

# Evaluate model
evaluation = trainer.evaluate_model_performance("Bitcoin")
```

## Detailed Training Instructions

### 1. LSTM Price Prediction Model

The LSTM model predicts cryptocurrency prices using historical data.

#### Data Requirements
- Historical price data with columns: Date, Open, High, Low, Close, Volume
- Minimum 100 days of data recommended
- Data should be sorted by date

#### Training Process
1. **Data Preprocessing**: Prices are normalized using MinMaxScaler
2. **Sequence Creation**: Creates 60-day sequences for prediction
3. **Model Architecture**: 2-layer LSTM with 50 hidden units
4. **Training**: Uses Adam optimizer with learning rate scheduling

#### Training Parameters
- `epochs`: Number of training iterations (default: 100)
- `batch_size`: Training batch size (default: 32)
- `learning_rate`: Initial learning rate (default: 0.001)
- `sequence_length`: Days to look back (fixed: 60)

#### Example Training Command
```bash
python train_models.py --model lstm --coin Bitcoin --epochs 200 --batch-size 64 --learning-rate 0.0005
```

#### Expected Output
- Model file: `trained_models/lstm_bitcoin_model.pth`
- Scaler file: `trained_models/lstm_bitcoin_scaler.pkl`
- Training metrics: MSE, MAE, loss curves

### 2. Sentiment Analysis Model

The sentiment model uses FinBERT for analyzing cryptocurrency news sentiment.

#### Model Details
- **Base Model**: ProsusAI/finbert
- **Task**: Sentiment classification (positive/negative/neutral)
- **Input**: News articles, social media posts
- **Output**: Sentiment label and confidence score

#### Training Process
1. **Model Loading**: Downloads FinBERT from Hugging Face
2. **Initialization**: Sets up tokenizer and classification pipeline
3. **Testing**: Validates with sample data

#### Training Command
```bash
python train_models.py --model sentiment --api-key YOUR_NEWSAPI_KEY
```

#### NewsAPI Setup (Optional)
1. Get API key from [NewsAPI.org](https://newsapi.org/)
2. Add to training command or environment variable
3. Enables real-time news fetching

#### Expected Output
- Model info: Device, max length, batch support
- Test results: Sample sentiment analysis
- Status: Initialized and ready for use

### 3. RAG Chatbot Model

The RAG model provides intelligent responses about cryptocurrencies using retrieval-augmented generation.

#### Model Details
- **Embedding Model**: all-MiniLM-L6-v2
- **Vector Database**: FAISS index
- **Knowledge Base**: Built from cryptocurrency datasets
- **Response Generation**: Context-aware responses

#### Training Process
1. **Data Loading**: Loads cryptocurrency datasets
2. **Knowledge Base Creation**: Extracts structured information
3. **Embedding Generation**: Creates vector embeddings
4. **Index Building**: Builds FAISS search index
5. **Testing**: Validates with sample queries

#### Training Command
```bash
python train_models.py --model rag --rebuild-index
```

#### Knowledge Base Structure
Each cryptocurrency entry includes:
- Basic information (name, symbol, price)
- Market cap analysis
- Trading volume analysis
- Price change information

#### Expected Output
- Index file: `trained_models/rag_index.index`
- Data file: `trained_models/rag_data.json`
- Model info: Index size, supported cryptocurrencies

## Training Results and Monitoring

### Output Files
All trained models are saved in the `trained_models/` directory:

```
trained_models/
├── lstm_bitcoin_model.pth          # LSTM model weights
├── lstm_bitcoin_scaler.pkl         # Data scaler
├── lstm_ethereum_model.pth        # Additional LSTM models...
├── rag_index.index                 # RAG search index
├── rag_data.json                   # RAG knowledge base
└── training_results.json           # Training summary
```

### Training Logs
Training progress is logged to:
- Console output (real-time)
- `training.log` file (detailed logs)

### Performance Metrics

#### LSTM Metrics
- **MSE (Mean Squared Error)**: Lower is better
- **MAE (Mean Absolute Error)**: Lower is better
- **Training Loss**: Should decrease over epochs
- **Validation Loss**: Should track training loss

#### Sentiment Metrics
- **Accuracy**: Classification accuracy
- **Confidence**: Model confidence in predictions
- **Response Time**: Processing speed

#### RAG Metrics
- **Index Size**: Number of knowledge entries
- **Search Accuracy**: Relevance of retrieved information
- **Response Quality**: Coherence of generated responses

## Troubleshooting

### Common Issues

#### 1. CUDA/GPU Issues
```bash
# If you get CUDA errors, force CPU usage
export CUDA_VISIBLE_DEVICES=""
python train_models.py --model all
```

#### 2. Memory Issues
```bash
# Reduce batch size for LSTM training
python train_models.py --model lstm --batch-size 16
```

#### 3. Dataset Not Found
```bash
# Check dataset directory structure
ls -la datasets/coins_datasets/
ls -la datasets/crypto_datasets/
```

#### 4. Model Loading Errors
```bash
# Rebuild models from scratch
rm -rf trained_models/
python train_models.py --model all
```

### Performance Optimization

#### For Better LSTM Performance
1. **Increase Training Data**: Use more historical data
2. **Tune Hyperparameters**: Experiment with epochs, learning rate
3. **Feature Engineering**: Add technical indicators
4. **Ensemble Methods**: Train multiple models

#### For Better Sentiment Analysis
1. **Use NewsAPI**: Get real-time news data
2. **Fine-tune Model**: Train on crypto-specific data
3. **Data Augmentation**: Increase training data variety

#### For Better RAG Performance
1. **Expand Knowledge Base**: Add more cryptocurrency data
2. **Improve Embeddings**: Use larger embedding models
3. **Query Optimization**: Improve search algorithms

## Advanced Usage

### Custom Training Configuration

Create a custom training configuration:

```python
# custom_training.py
from train_models import ModelTrainer

trainer = ModelTrainer()

# Custom LSTM training
custom_results = trainer.train_lstm_model(
    coin_symbol="Bitcoin",
    epochs=300,
    batch_size=64,
    learning_rate=0.0005
)

# Custom evaluation
evaluation = trainer.evaluate_model_performance("Bitcoin")
print(f"Model performance: {evaluation}")
```

### Batch Training Script

For training multiple models with different parameters:

```bash
#!/bin/bash
# batch_train.sh

coins=("Bitcoin" "Ethereum" "Cardano" "Solana")

for coin in "${coins[@]}"; do
    echo "Training LSTM for $coin"
    python train_models.py --model lstm --coin "$coin" --epochs 150
done
```

### Model Comparison

Compare different model configurations:

```python
# model_comparison.py
from train_models import ModelTrainer

trainer = ModelTrainer()

# Train with different parameters
configs = [
    {"epochs": 100, "batch_size": 32, "learning_rate": 0.001},
    {"epochs": 200, "batch_size": 64, "learning_rate": 0.0005},
    {"epochs": 150, "batch_size": 16, "learning_rate": 0.002}
]

results = []
for i, config in enumerate(configs):
    result = trainer.train_lstm_model("Bitcoin", **config)
    results.append({f"config_{i}": result})

print("Model comparison results:", results)
```

## Next Steps

After training your models:

1. **Test the Models**: Use the evaluation functions to test performance
2. **Deploy Models**: Integrate trained models into your API
3. **Monitor Performance**: Track model performance over time
4. **Retrain Periodically**: Update models with new data
5. **Fine-tune Parameters**: Optimize based on performance metrics

## Support

If you encounter issues:

1. Check the training logs in `training.log`
2. Verify dataset structure and format
3. Ensure all dependencies are installed
4. Check available system resources (RAM, disk space)
5. Review error messages for specific guidance

Happy training! 🚀
