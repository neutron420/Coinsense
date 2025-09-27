# 🚀 Crypto AI Chatbot Backend

A comprehensive AI-powered cryptocurrency analysis and assistance backend built with FastAPI, featuring advanced machine learning models for price prediction, sentiment analysis, and intelligent chat capabilities.

## 🎯 Features

### 🤖 AI-Powered Chatbot (RAG)
- **Retrieval-Augmented Generation** using Sentence Transformers
- **FAISS vector search** for fast similarity matching
- **395+ cryptocurrency knowledge base** from Kaggle datasets
- Intelligent responses about crypto concepts, trading, DeFi, staking, wallets

### 📈 LSTM Price Prediction
- **PyTorch LSTM neural network** for cryptocurrency price forecasting
- **Historical data analysis** from multiple crypto datasets
- **Confidence scoring** for prediction reliability
- Support for **20+ major cryptocurrencies**

### 📊 FinBERT Sentiment Analysis
- **Pre-trained FinBERT model** for financial sentiment analysis
- **Real-time news analysis** from NewsAPI
- **Market sentiment tracking** and trend analysis
- **Confidence scoring** for sentiment predictions

### 🔐 Authentication & Security
- **JWT-based authentication** with secure token management
- **Password hashing** with bcrypt
- **User session management** and chat history
- **CORS protection** and input sanitization

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment variables
│   ├── database.py          # PostgreSQL database connection
│   ├── models.py            # SQLAlchemy database models
│   ├── utils.py             # Utility functions and helpers
│   ├── auth.py              # Authentication and authorization
│   ├── ml/                  # Machine Learning models
│   │   ├── lstm_model.py    # LSTM price prediction model
│   │   ├── rag_nlp.py       # RAG chatbot implementation
│   │   └── sentiment_model.py # FinBERT sentiment analysis
│   └── routes/              # API route handlers
│       ├── auth.py          # Authentication endpoints
│       ├── chat.py          # Chat and RAG endpoints
│       ├── predict.py       # Price prediction endpoints
│       └── sentiment.py     # Sentiment analysis endpoints
├── datasets/                # Cryptocurrency datasets
├── models/                  # Trained model storage
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- 8GB+ RAM (for ML models)

### Installation

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp env_example.txt .env
# Edit .env with your configuration
```

5. **Set up PostgreSQL database:**
```sql
CREATE DATABASE coinsense_db;
CREATE USER coinsense_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE coinsense_db TO coinsense_user;
```

6. **Update .env file:**
```env
DATABASE_URL=postgresql://coinsense_user:your_password@localhost:5432/coinsense_db
SECRET_KEY=your-super-secret-jwt-key
COINGECKO_API_KEY=your-coingecko-api-key
NEWS_API_KEY=your-newsapi-key
```

7. **Run the application:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

#### Chat & RAG
- `POST /api/chat/message` - Send message to chatbot
- `GET /api/chat/history` - Get chat history
- `GET /api/chat/sessions` - Get chat sessions

#### Price Prediction
- `POST /api/predict/predict` - Predict cryptocurrency price
- `GET /api/predict/history` - Get prediction history
- `GET /api/predict/supported-symbols` - Get supported cryptocurrencies

#### Sentiment Analysis
- `POST /api/sentiment/analyze` - Analyze text sentiment
- `POST /api/sentiment/market-sentiment` - Get market sentiment
- `GET /api/sentiment/crypto-sentiment/{crypto_name}` - Get crypto-specific sentiment

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://username:password@localhost:5432/coinsense_db` |
| `SECRET_KEY` | JWT secret key | `your-super-secret-jwt-key-change-this-in-production` |
| `COINGECKO_API_KEY` | CoinGecko API key | `your-coingecko-api-key` |
| `NEWS_API_KEY` | NewsAPI key | `your-newsapi-key` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `True` |

### Model Configuration

- **LSTM Model:** 60-day sequence length, 50 hidden units, 2 layers
- **RAG Model:** all-MiniLM-L6-v2 sentence transformer
- **Sentiment Model:** ProsusAI/finbert for financial sentiment

## 📊 Data Sources

### Cryptocurrency Datasets
- **Price Data:** Historical OHLCV data for 20+ cryptocurrencies
- **Market Data:** 395+ cryptocurrency dataset with market cap, volume, etc.
- **Real-time Data:** CoinGecko API for live prices

### News Sources
- **NewsAPI:** Real-time cryptocurrency news
- **FinBERT:** Pre-trained financial sentiment model

## 🧠 Machine Learning Models

### LSTM Price Prediction
```python
# Model Architecture
- Input: 60-day price sequences
- LSTM: 2 layers, 50 hidden units
- Output: Next-day price prediction
- Confidence: Based on recent volatility
```

### RAG Chatbot
```python
# RAG Pipeline
- Knowledge Base: 395+ cryptocurrency dataset
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
- Search: FAISS vector similarity
- Generation: Contextual response generation
```

### FinBERT Sentiment Analysis
```python
# Sentiment Pipeline
- Model: ProsusAI/finbert
- Input: News articles and text
- Output: Positive/Negative/Neutral with confidence
- Confidence: Model prediction probability
```

## 🔒 Security Features

- **JWT Authentication:** Secure token-based authentication
- **Password Hashing:** bcrypt with salt
- **Input Sanitization:** XSS and injection protection
- **CORS Protection:** Configurable origin restrictions
- **Rate Limiting:** Request rate limiting (configurable)

## 📈 Performance

- **FastAPI:** High-performance async framework
- **FAISS:** Fast vector similarity search
- **PostgreSQL:** Robust relational database
- **Caching:** Model and data caching
- **Async Processing:** Non-blocking I/O operations

## 🚀 Deployment

### Docker (Recommended)
```bash
docker build -t crypto-ai-chatbot .
docker run -p 8000:8000 crypto-ai-chatbot
```

### Production Setup
1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies
4. Run database migrations
5. Start with production WSGI server

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the configuration guide above

## 🎉 Acknowledgments

- **FastAPI** for the excellent web framework
- **Hugging Face** for pre-trained models
- **Kaggle** for cryptocurrency datasets
- **CoinGecko** and **NewsAPI** for real-time data
- **FAISS** for efficient vector search

---

**Built with ❤️ for the cryptocurrency community**
