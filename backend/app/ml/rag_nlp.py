"""
RAG (Retrieval-Augmented Generation) Chatbot for Cryptocurrency Knowledge
"""
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
import json
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime
import re

# Configure logging
logger = logging.getLogger(__name__)

class CryptoRAGChatbot:
    """RAG-based chatbot for cryptocurrency knowledge"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = None, data_path: str = None):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.data = None
        self.index_path = index_path
        self.data_path = data_path

        # Load or create index
        if index_path and os.path.exists(index_path):
            self.load_index()
        else:
            # Build index from all datasets in the specified directory
            dataset_dir = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'crypto_datasets')
            self.build_index_from_directory(dataset_dir)

    def load_crypto_dataset(self, csv_path: str) -> pd.DataFrame:
        """Load cryptocurrency dataset"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded dataset with {len(df)} records from {csv_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better embedding"""
        if pd.isna(text):
            return ""
        
        # Convert to string and clean
        text = str(text).strip()
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\.\,\!\?\-\$\%]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text

    def create_knowledge_base(self, df: pd.DataFrame) -> List[Dict]:
        """Create knowledge base from cryptocurrency dataset"""
        knowledge_base = []
        
        try:
            for _, row in df.iterrows():
                # Create multiple knowledge entries per cryptocurrency
                symbol = str(row.get('Symbol', '')).strip()
                name = str(row.get('Name', '')).strip()
                
                if not symbol or symbol == 'nan':
                    continue
                
                # Basic information
                basic_info = {
                    'id': f"{symbol}_basic",
                    'text': f"{name} ({symbol}) is a cryptocurrency. Current price: ${row.get('Price (Intraday)', 'N/A')}. Market cap: {row.get('Market Cap', 'N/A')}. Volume: {row.get('Volume in Currency (24Hr)', 'N/A')}.",
                    'metadata': {
                        'type': 'basic_info',
                        'symbol': symbol,
                        'name': name,
                        'price': row.get('Price (Intraday)', ''),
                        'market_cap': row.get('Market Cap', ''),
                        'volume': row.get('Volume in Currency (24Hr)', '')
                    }
                }
                knowledge_base.append(basic_info)
                
                # Price change information
                price_change = row.get('% Change', '')
                if price_change and price_change != 'nan':
                    change_info = {
                        'id': f"{symbol}_change",
                        'text': f"{name} ({symbol}) has changed by {price_change} in the last 24 hours. The price change is {row.get('Change', 'N/A')}.",
                        'metadata': {
                            'type': 'price_change',
                            'symbol': symbol,
                            'name': name,
                            'change_percent': price_change,
                            'change_amount': row.get('Change', '')
                        }
                    }
                    knowledge_base.append(change_info)
                
                # Market cap information
                market_cap = row.get('Market Cap', '')
                if market_cap and market_cap != 'nan':
                    cap_info = {
                        'id': f"{symbol}_market_cap",
                        'text': f"{name} ({symbol}) has a market capitalization of {market_cap}. This makes it one of the {self._get_market_cap_tier(market_cap)} cryptocurrencies.",
                        'metadata': {
                            'type': 'market_cap',
                            'symbol': symbol,
                            'name': name,
                            'market_cap': market_cap
                        }
                    }
                    knowledge_base.append(cap_info)
                
                # Volume information
                volume = row.get('Volume in Currency (24Hr)', '')
                if volume and volume != 'nan':
                    volume_info = {
                        'id': f"{symbol}_volume",
                        'text': f"{name} ({symbol}) has a 24-hour trading volume of {volume}. This indicates {self._get_volume_analysis(volume)} trading activity.",
                        'metadata': {
                            'type': 'volume',
                            'symbol': symbol,
                            'name': name,
                            'volume': volume
                        }
                    }
                    knowledge_base.append(volume_info)
            
            logger.info(f"Created knowledge base with {len(knowledge_base)} entries")
            return knowledge_base
        
        except Exception as e:
            logger.error(f"Error creating knowledge base: {e}")
            raise

    def _get_market_cap_tier(self, market_cap: str) -> str:
        """Determine market cap tier"""
        try:
            # Extract numeric value
            numeric_value = float(re.sub(r'[^\d\.]', '', market_cap))
            
            if 'T' in market_cap.upper():
                if numeric_value > 100:
                    return "largest"
                elif numeric_value > 10:
                    return "major"
                else:
                    return "significant"
            elif 'B' in market_cap.upper():
                if numeric_value > 50:
                    return "major"
                elif numeric_value > 10:
                    return "significant"
                else:
                    return "moderate"
            else:
                return "smaller"
        except:
            return "unknown"
    
    def _get_volume_analysis(self, volume: str) -> str:
        """Analyze trading volume"""
        try:
            numeric_value = float(re.sub(r'[^\d\.]', '', volume))
            
            if 'B' in volume.upper():
                if numeric_value > 5:
                    return "very high"
                elif numeric_value > 1:
                    return "high"
                else:
                    return "moderate"
            elif 'M' in volume.upper():
                if numeric_value > 500:
                    return "high"
                elif numeric_value > 100:
                    return "moderate"
                else:
                    return "low"
            else:
                return "very low"
        except:
            return "unknown"
            
    def build_index_from_directory(self, directory_path: str):
        """Build FAISS index from all CSV files in a directory."""
        try:
            csv_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.csv')]
            if not csv_files:
                raise ValueError("No CSV files found in the specified directory.")

            all_dfs = [self.load_crypto_dataset(csv_file) for csv_file in csv_files]
            df = pd.concat(all_dfs, ignore_index=True)

            # Remove duplicate entries based on 'Symbol', keeping the last one
            df.drop_duplicates(subset=['Symbol'], keep='last', inplace=True)

            self.data = self.create_knowledge_base(df)
            
            texts = [item['text'] for item in self.data]
            embeddings = self.model.encode(texts)
            
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"Built FAISS index with {self.index.ntotal} vectors from {len(csv_files)} files.")

        except Exception as e:
            logger.error(f"Error building index from directory: {e}")
            raise

    def save_index(self, index_path: str, data_path: str):
        """Save FAISS index and data"""
        try:
            if self.index is None or self.data is None:
                raise ValueError("No index or data to save")
            
            # Create directories
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, index_path)
            
            # Save data
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Index saved to {index_path}")
            logger.info(f"Data saved to {data_path}")
        
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise

    def load_index(self):
        """Load FAISS index and data"""
        try:
            if not self.index_path or not os.path.exists(self.index_path):
                raise ValueError("Index path not provided or file doesn't exist")
            
            # Load FAISS index
            self.index = faiss.read_index(self.index_path)
            
            # Load data
            data_file = self.index_path.replace('.index', '_data.json')
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            
            logger.info(f"Loaded index with {self.index.ntotal} vectors")
        
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant information"""
        try:
            if self.index is None or self.data is None:
                raise ValueError("Index not loaded")
            
            # Encode query
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.data):
                    result = self.data[idx].copy()
                    result['similarity_score'] = float(score)
                    results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise

    def generate_response(self, query: str, context_limit: int = 3) -> Dict:
        """Generate response using RAG"""
        try:
            # Search for relevant context
            search_results = self.search(query, top_k=context_limit)
            
            if not search_results:
                return {
                    'response': "I don't have specific information about that cryptocurrency. Could you please rephrase your question or ask about a different cryptocurrency?",
                    'confidence': 0.0,
                    'sources': []
                }
            
            # Extract context
            context = []
            sources = []
            total_confidence = 0
            
            for result in search_results:
                context.append(result['text'])
                sources.append({
                    'text': result['text'],
                    'similarity_score': result['similarity_score'],
                    'metadata': result.get('metadata', {})
                })
                total_confidence += result['similarity_score']
            
            # Generate response
            response = self._generate_contextual_response(query, context)
            avg_confidence = total_confidence / len(search_results)
            
            return {
                'response': response,
                'confidence': float(avg_confidence),
                'sources': sources,
                'context_used': len(context)
            }
        
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return {
                'response': "I'm sorry, I encountered an error while processing your request. Please try again.",
                'confidence': 0.0,
                'sources': []
            }

    def _generate_contextual_response(self, query: str, context: List[str]) -> str:
        """Generate contextual response based on query and context"""
        query_lower = query.lower()
        
        # Price-related queries
        if any(word in query_lower for word in ['price', 'cost', 'value', 'worth', 'expensive', 'cheap']):
            return self._generate_price_response(query, context)
        
        # Market cap queries
        elif any(word in query_lower for word in ['market cap', 'market capitalization', 'size', 'biggest', 'largest']):
            return self._generate_market_cap_response(query, context)
        
        # Volume queries
        elif any(word in query_lower for word in ['volume', 'trading', 'activity', 'popular']):
            return self._generate_volume_response(query, context)
        
        # Change/performance queries
        elif any(word in query_lower for word in ['change', 'up', 'down', 'increase', 'decrease', 'performance']):
            return self._generate_change_response(query, context)
        
        # General information
        else:
            return self._generate_general_response(query, context)

    def _generate_price_response(self, query: str, context: List[str]) -> str:
        """Generate response for price-related queries"""
        response_parts = []
        
        for ctx in context:
            if 'price' in ctx.lower():
                response_parts.append(ctx)
        
        if response_parts:
            return " ".join(response_parts[:2])  # Limit to 2 most relevant contexts
        else:
            return "I don't have current price information for that cryptocurrency. Please check a reliable cryptocurrency exchange for the most up-to-date prices."

    def _generate_market_cap_response(self, query: str, context: List[str]) -> str:
        """Generate response for market cap queries"""
        response_parts = []
        
        for ctx in context:
            if 'market cap' in ctx.lower() or 'market capitalization' in ctx.lower():
                response_parts.append(ctx)
        
        if response_parts:
            return " ".join(response_parts[:2])
        else:
            return "I don't have market capitalization information for that cryptocurrency."

    def _generate_volume_response(self, query: str, context: List[str]) -> str:
        """Generate response for volume queries"""
        response_parts = []
        
        for ctx in context:
            if 'volume' in ctx.lower() or 'trading' in ctx.lower():
                response_parts.append(ctx)
        
        if response_parts:
            return " ".join(response_parts[:2])
        else:
            return "I don't have trading volume information for that cryptocurrency."

    def _generate_change_response(self, query: str, context: List[str]) -> str:
        """Generate response for price change queries"""
        response_parts = []
        
        for ctx in context:
            if 'change' in ctx.lower() or '%' in ctx:
                response_parts.append(ctx)
        
        if response_parts:
            return " ".join(response_parts[:2])
        else:
            return "I don't have recent price change information for that cryptocurrency."

    def _generate_general_response(self, query: str, context: List[str]) -> str:
        """Generate general response"""
        if context:
            return f"Based on the available information: {context[0]}"
        else:
            return "I don't have specific information about that. Could you please ask about a specific cryptocurrency or rephrase your question?"

    def get_supported_cryptocurrencies(self) -> List[str]:
        """Get list of supported cryptocurrencies"""
        if not self.data:
            return []
        
        symbols = set()
        for item in self.data:
            metadata = item.get('metadata', {})
            symbol = metadata.get('symbol')
            if symbol:
                symbols.add(symbol)
        
        return sorted(list(symbols))

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'index_size': self.index.ntotal if self.index else 0,
            'data_size': len(self.data) if self.data else 0,
            'supported_cryptocurrencies': len(self.get_supported_cryptocurrencies())
        }

# Global chatbot instance
chatbot = None

def get_chatbot() -> CryptoRAGChatbot:
    global chatbot
    if chatbot is None:
        chatbot = CryptoRAGChatbot()
    return chatbot