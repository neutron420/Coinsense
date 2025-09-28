
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
import os
from typing import List, Tuple, Dict, Optional
import logging
from datetime import datetime, timedelta
import requests
import json

# Configure logging
logger = logging.getLogger(__name__)

class LSTMModel(nn.Module):
    """LSTM model for cryptocurrency price prediction"""

    def __init__(self, input_size: int = 1, hidden_size: int = 50, num_layers: int = 2, output_size: int = 1, dropout: float = 0.2):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # LSTM layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)

        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 25)
        self.fc2 = nn.Linear(25, output_size)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()

    def forward(self, x):
        # Initialize hidden state
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        # LSTM forward pass
        out, _ = self.lstm(x, (h0, c0))

        # Take the last output
        out = out[:, -1, :]

        # Fully connected layers
        out = self.dropout(out)
        out = self.fc1(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)

        return out

class CryptoPricePredictor:
    """Cryptocurrency price prediction using LSTM"""

    def __init__(self, model_path: str = None, scaler_path: str = None):
        self.model = None
        self.scaler = MinMaxScaler()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.sequence_length = 60  # Number of days to look back
        self.model_path = model_path
        self.scaler_path = scaler_path

        # Load model and scaler if paths provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        if scaler_path and os.path.exists(scaler_path):
            self.load_scaler(scaler_path)

    def prepare_data(self, df: pd.DataFrame, target_column: str = 'Close') -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for LSTM training"""
        try:
            # Extract price data
            prices = df[target_column].values.reshape(-1, 1)

            # Scale the data
            scaled_prices = self.scaler.fit_transform(prices)

            # Create sequences
            X, y = [], []
            for i in range(self.sequence_length, len(scaled_prices)):
                X.append(scaled_prices[i-self.sequence_length:i])
                y.append(scaled_prices[i])

            return np.array(X), np.array(y)

        except Exception as e:
            logger.error(f"Data preparation error: {e}")
            raise

    def train_model(self, df: pd.DataFrame, epochs: int = 100, batch_size: int = 32, learning_rate: float = 0.001) -> Dict:
        """Train the LSTM model"""
        try:
            # Prepare data
            X, y = self.prepare_data(df)

            # Split data
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            # Convert to tensors
            X_train = torch.FloatTensor(X_train).to(self.device)
            y_train = torch.FloatTensor(y_train).to(self.device)
            X_test = torch.FloatTensor(X_test).to(self.device)
            y_test = torch.FloatTensor(y_test).to(self.device)

            # Initialize model
            self.model = LSTMModel(input_size=1, hidden_size=50, num_layers=2, output_size=1)
            self.model.to(self.device)

            # Loss and optimizer
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)

            # Training loop
            train_losses = []
            test_losses = []

            for epoch in range(epochs):
                # Training
                self.model.train()
                optimizer.zero_grad()
                outputs = self.model(X_train)
                loss = criterion(outputs, y_train)
                loss.backward()
                optimizer.step()

                # Validation
                self.model.eval()
                with torch.no_grad():
                    test_outputs = self.model(X_test)
                    test_loss = criterion(test_outputs, y_test)

                train_losses.append(loss.item())
                test_losses.append(test_loss.item())
                scheduler.step(test_loss)

                if epoch % 10 == 0:
                    logger.info(f"Epoch {epoch}, Train Loss: {loss.item():.6f}, Test Loss: {test_loss.item():.6f}")

            # Calculate metrics
            self.model.eval()
            with torch.no_grad():
                train_pred = self.model(X_train).cpu().numpy()
                test_pred = self.model(X_test).cpu().numpy()

                # Inverse transform
                train_pred = self.scaler.inverse_transform(train_pred)
                test_pred = self.scaler.inverse_transform(test_pred)
                y_train_orig = self.scaler.inverse_transform(y_train.cpu().numpy())
                y_test_orig = self.scaler.inverse_transform(y_test.cpu().numpy())

                # Calculate metrics
                train_mse = mean_squared_error(y_train_orig, train_pred)
                test_mse = mean_squared_error(y_test_orig, test_pred)
                train_mae = mean_absolute_error(y_train_orig, train_pred)
                test_mae = mean_absolute_error(y_test_orig, test_pred)

            metrics = {
                'train_mse': train_mse,
                'test_mse': test_mse,
                'train_mae': train_mae,
                'test_mae': test_mae,
                'final_train_loss': train_losses[-1],
                'final_test_loss': test_losses[-1]
            }

            logger.info(f"Training completed. Metrics: {metrics}")
            return metrics

        except Exception as e:
            logger.error(f"Training error: {e}")
            raise

    def predict_price(self, df: pd.DataFrame, days_ahead: int = 1) -> Dict:
        """Predict future cryptocurrency prices"""
        try:
            if self.model is None:
                raise ValueError("Model not trained or loaded")

            # Get the last sequence
            last_sequence = df['Close'].tail(self.sequence_length).values.reshape(-1, 1)
            last_sequence_scaled = self.scaler.transform(last_sequence)

            # Prepare for prediction
            X = torch.FloatTensor(last_sequence_scaled).unsqueeze(0).to(self.device)

            predictions = []
            current_sequence = last_sequence_scaled.copy()

            self.model.eval()
            with torch.no_grad():
                for _ in range(days_ahead):
                    # Predict next value
                    pred = self.model(torch.FloatTensor(current_sequence).unsqueeze(0).to(self.device))
                    pred_value = pred.cpu().numpy()
                    predictions.append(pred_value[0, 0])

                    # Update sequence for next prediction
                    current_sequence = np.roll(current_sequence, -1, axis=0)
                    current_sequence[-1] = pred_value[0, 0]

            # Inverse transform predictions
            predictions = np.array(predictions).reshape(-1, 1)
            predictions = self.scaler.inverse_transform(predictions)

            # Calculate confidence based on recent volatility
            recent_prices = df['Close'].tail(30).values
            volatility = np.std(recent_prices) / np.mean(recent_prices)
            confidence = max(0.1, min(0.9, 1 - volatility))

            return {
                'predictions': predictions.flatten().tolist(),
                'confidence': float(confidence),
                'current_price': float(df['Close'].iloc[-1]),
                'prediction_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise

    def save_model(self, model_path: str, scaler_path: str):
        """Save model and scaler"""
        try:
            if self.model is None:
                raise ValueError("No model to save")

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            os.makedirs(os.path.dirname(scaler_path), exist_ok=True)

            # Save model
            torch.save(self.model.state_dict(), model_path)

            # Save scaler
            joblib.dump(self.scaler, scaler_path)

            logger.info(f"Model saved to {model_path}")
            logger.info(f"Scaler saved to {scaler_path}")

        except Exception as e:
            logger.error(f"Model saving error: {e}")
            raise

    def load_model(self, model_path: str):
        """Load model"""
        try:
            self.model = LSTMModel(input_size=1, hidden_size=50, num_layers=2, output_size=1)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Model loaded from {model_path}")

        except Exception as e:
            logger.error(f"Model loading error: {e}")
            raise

    def load_scaler(self, scaler_path: str):
        """Load scaler"""
        try:
            self.scaler = joblib.load(scaler_path)
            logger.info(f"Scaler loaded from {scaler_path}")

        except Exception as e:
            logger.error(f"Scaler loading error: {e}")
            raise

    def get_model_info(self) -> Dict:
        """Get model information"""
        if self.model is None:
            return {"status": "No model loaded"}

        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        return {
            "model_type": "LSTM",
            "input_size": 1,
            "hidden_size": 50,
            "num_layers": 2,
            "sequence_length": self.sequence_length,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "device": str(self.device)
        }

# Global predictor instance
predictor = None

def get_predictor() -> CryptoPricePredictor:
    """Get or create global predictor instance"""
    global predictor
    if predictor is None:
        predictor = CryptoPricePredictor()
    return predictor

def load_crypto_data(symbol: str, days: int = 365) -> pd.DataFrame:
    """Load cryptocurrency data from CSV files"""
    try:
        # Sanitize the symbol to get the coin name for the file
        # e.g., 'BTC' -> 'Bitcoin', 'ETH' -> 'Ethereum'
        # This part might need a mapping if the symbol doesn't directly map to the file name's capitalization
        coin_name = symbol.capitalize() # Simple capitalization, adjust if needed
        filename = f"coin_{coin_name}.csv"
        
        # Construct the full path to the data file
        data_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'coins_datasets', filename)
        
        if not os.path.exists(data_path):
             # Try to find a file that matches case-insensitively
            files_in_dir = os.listdir(os.path.join(os.path.dirname(__file__), '..', 'datasets', 'coins_datasets'))
            matching_file = next((f for f in files_in_dir if f.lower() == filename.lower()), None)
            if not matching_file:
                raise ValueError(f"No data file found for symbol: {symbol}")
            data_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'coins_datasets', matching_file)

        df = pd.read_csv(data_path)

        # Convert date column
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        # Select required columns
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df[required_columns]

        # Remove any rows with missing values
        df = df.dropna()

        # Take last N days
        if len(df) > days:
            df = df.tail(days)

        logger.info(f"Loaded {len(df)} records for {symbol}")
        return df

    except Exception as e:
        logger.error(f"Data loading error for {symbol}: {e}")
        raise